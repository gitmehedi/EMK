# imports of odoo
from odoo import models, fields, api, _


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    amount_total = fields.Float(string='Total', store=True, readonly=True, compute='_compute_amount')

    @api.depends('bom_line_ids.price_subtotal')
    def _compute_amount(self):
        self.amount_total = sum(line.price_subtotal for line in self.bom_line_ids)


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    price_unit = fields.Float(string='Unit Price')
    price_subtotal = fields.Float(string='Amount', store=True, readonly=True, compute='_compute_price')

    @api.depends('product_qty', 'price_unit')
    def _compute_price(self):
        for rec in self:
            rec.price_subtotal = rec.price_unit * rec.product_qty

    @api.onchange('product_id')
    def onchange_product_id(self):
        super(MrpBomLine, self).onchange_product_id()
        if self.product_id:
            self.price_unit = self.product_id.uom_id._compute_price(self.product_id.standard_price, self.product_uom_id)
