# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    amount_total = fields.Float(string='Total', store=True, readonly=True, compute='_compute_amount')

    @api.depends('bom_line_ids.price_subtotal')
    def _compute_amount(self):
        for rec in self:
            rec.amount_total = sum(line.price_subtotal for line in rec.bom_line_ids)

    @api.constrains('bom_line_ids')
    def _check_bom_line_ids(self):
        if len(self.bom_line_ids.ids) <= 0:
            raise ValidationError(_("can not create Bill of Materials without Product line !!!"))

        if self.bom_line_ids.ids:
            product_names = set()
            for line in self.bom_line_ids:
                if line.price_unit <= 0:
                    product_names.add(str(line.product_id.product_tmpl_id.name))

            if len(product_names) > 0:
                raise ValidationError(_('In Product line, the value of Unit Price must be greater than 0 '
                                        'for the following product(s):\n => %s') % str(tuple(product_names))[1:-1])


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    price_unit = fields.Float(string='Unit Price', store=True, readonly=True, compute='_compute_price_unit')
    price_subtotal = fields.Float(string='Amount', store=True, readonly=True, compute='_compute_price')

    @api.depends('product_id', 'product_uom_id')
    def _compute_price_unit(self):
        for rec in self:
            if rec.product_id:
                rec.price_unit = rec.product_id.uom_id._compute_price(rec.product_id.standard_price, rec.product_uom_id)

    @api.depends('product_qty', 'price_unit')
    def _compute_price(self):
        for rec in self:
            rec.price_subtotal = rec.price_unit * rec.product_qty
