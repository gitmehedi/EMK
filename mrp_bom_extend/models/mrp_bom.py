# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('historical', 'Historical')
    ], string='State', readonly=True, default='draft', track_visibility='onchange')
    # amount_total = fields.Float(string='Total', store=True, readonly=True, compute='_compute_amount')

    # @api.depends('bom_line_ids.price_subtotal')
    # def _compute_amount(self):
    #     for rec in self:
    #         rec.amount_total = sum(line.price_subtotal for line in rec.bom_line_ids)

    @api.constrains('product_id', 'product_tmpl_id', 'bom_line_ids')
    def _check_product_recursion(self):
        pass

    @api.constrains('product_qty')
    def _check_product_qty(self):
        if self.product_qty <= 0:
            raise ValidationError(_("Quantity must be greater than 0."))

    @api.constrains('bom_line_ids')
    def _check_bom_line_ids(self):
        if len(self.bom_line_ids.ids) <= 0:
            raise ValidationError(_("can not create Bill of Materials without Product line !!!"))

        # if self.bom_line_ids.ids:
        #     product_names = set()
        #     for line in self.bom_line_ids:
        #         if line.price_unit <= 0:
        #             product_names.add(str(line.product_id.product_tmpl_id.name))
        #
        #     if len(product_names) > 0:
        #         raise ValidationError(_('In Product line, the value of Unit Price must be greater than 0 '
        #                                 'for the following product(s):\n => %s') % str(tuple(product_names))[1:-1])

    @api.model
    def _bom_find(self, product_tmpl=None, product=None, picking_type=None, company_id=False):
        """ Finds BoM for particular product, picking and company """
        if product:
            if not product_tmpl:
                product_tmpl = product.product_tmpl_id
            domain = ['&', ('state', '=', 'confirmed'), '|', ('product_id', '=', product.id), '&', ('product_id', '=', False), ('product_tmpl_id', '=', product_tmpl.id)]
        elif product_tmpl:
            domain = [('product_tmpl_id', '=', product_tmpl.id)]
        else:
            # neither product nor template, makes no sense to search
            return False
        if picking_type:
            domain += ['|', ('picking_type_id', '=', picking_type.id), ('picking_type_id', '=', False)]
        if company_id or self.env.context.get('company_id'):
            domain = domain + [('company_id', '=', company_id or self.env.context.get('company_id'))]
        # order to prioritize bom with product_id over the one without
        return self.search(domain, order='sequence, product_id', limit=1)


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    # price_unit = fields.Float(string='Unit Price', store=True, readonly=True, compute='_compute_price_unit')
    # price_subtotal = fields.Float(string='Amount', store=True, readonly=True, compute='_compute_price')
    categ_id = fields.Many2one('product.category', 'Internal Category', store=False, compute='_compute_categ_id')

    _sql_constraints = [
        ('bom_qty_zero', 'CHECK (product_qty>0)', 'All product quantities must be greater than 0.'),
    ]

    # @api.depends('product_id', 'product_uom_id')
    # def _compute_price_unit(self):
    #     for rec in self:
    #         if rec.product_id:
    #             rec.price_unit = rec.product_id.uom_id._compute_price(rec.product_id.standard_price, rec.product_uom_id)
    #
    # @api.depends('product_qty', 'price_unit')
    # def _compute_price(self):
    #     for rec in self:
    #         rec.price_subtotal = rec.price_unit * rec.product_qty

    @api.depends('product_id')
    def _compute_categ_id(self):
        for rec in self:
            if rec.product_id:
                rec.categ_id = rec.product_id.categ_id.id
