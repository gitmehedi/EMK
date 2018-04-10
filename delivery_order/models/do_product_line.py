from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class DOProductLine(models.Model):
    _name = 'delivery.order.line'
    _description = 'Sales Delivery Authorization line'

    product_id = fields.Many2one('product.product', string="Product", readonly=True, ondelete='cascade')
    uom_id = fields.Many2one('product.uom', string="UoM", ondelete='cascade', readonly=True)
    pack_type = fields.Many2one('product.packaging.mode', string="Packing", ondelete='cascade', readonly=True)
    quantity = fields.Float(string="Delivery Qty", required=True, default=1)
    price_unit = fields.Float(string="Price Unit", readonly=True)
    commission_rate = fields.Float(string="Commission", readonly=True)
    price_subtotal = fields.Float(string="Subtotal", readonly=True)
    tax_id = fields.Many2one('account.tax', string='Tax', readonly=True)

    """ Relational Fields """
    parent_id = fields.Many2one('delivery.order', ondelete='cascade')
    state = fields.Selection([
        ('draft', "To Submit"),
        ('validate', "To Approve"),
        ('approve', "Second Approval"),
        ('close', "Approved")
    ], default='draft')

    deli_mode = fields.Selection([
        ('bonded', 'Bonded'),
        ('non_bonded', 'Non-bonded'),
        ('vat', 'VAT'),
    ], string='Delivery Mode')

    @api.multi
    @api.constrains('quantity')
    def check_quantity(self):
        for da in self:
            if da.quantity < 0.00:
                raise ValidationError('Quantity can not be negative')

            for sale_line in da.parent_id.sale_order_id.order_line:
                if da.product_id.id == sale_line.product_id.id:
                    if da.quantity > sale_line.product_uom_qty:
                        raise ValidationError('Delivery Qty can not be greater than Ordered Qty')

                    # if da.quantity > sale_line.da_qty:
                    #     raise ValidationError('You can Deliver {0} {1} for {2}'.format((sale_line.da_qty), (sale_line.product_uom.name), (sale_line.product_id.display_name)))

            da.set_da_amounts_automatically()

    @api.onchange('quantity')
    def onchange_quantity(self):
        self.set_da_amounts_automatically()

    @api.one
    def set_da_amounts_automatically(self):
        if self.quantity:
            self.price_subtotal = self.price_unit * self.quantity
            self.parent_id.amount_untaxed = self.price_subtotal
            self.parent_id.tax_value = self.price_subtotal * (self.tax_id.amount / 100)
            self.parent_id.total_amount = self.parent_id.tax_value + self.price_subtotal

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            product_obj = self.env['product.template'].search([('id', '=', self.product_id.id)])
            if product_obj:
                self.uom_id = product_obj.uom_id.id
