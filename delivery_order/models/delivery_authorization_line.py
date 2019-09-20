from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp


class DeliveryAuthorizationLine(models.Model):
    _name = 'delivery.authorization.line'
    _description = 'Delivery Authorization line'

    product_id = fields.Many2one('product.product', string="Product", readonly=True, ondelete='cascade')
    uom_id = fields.Many2one('product.uom', string="UoM", ondelete='cascade', readonly=True)
    pack_type = fields.Many2one('product.packaging.mode', string="Packing", ondelete='cascade', readonly=True)
    quantity = fields.Float(string="Ordered Qty", readonly=True, required=True, default=1)
    price_unit = fields.Float(string="Price Unit", readonly=True,digits=dp.get_precision('Product Price'))
    commission_rate = fields.Float(string="Commission", readonly=True)
    price_subtotal = fields.Float(string="Subtotal", readonly=True)
    tax_id = fields.Many2one('account.tax', string='Tax', readonly=True)

    """ Relational Fields """
    parent_id = fields.Many2one('delivery.authorization', ondelete='cascade')
    # state = fields.Selection([
    #     ('draft', "To Submit"),
    #     ('validate', "To Approve"),
    #     ('approve', "Second Approval"),
    #     ('close', "Approved")
    # ], default='draft')

    deli_mode = fields.Selection([
        ('bonded', 'Bonded'),
        ('non_bonded', 'Non-bonded'),
        ('vat', 'VAT'),
    ], string='Delivery Mode')

    delivery_qty = fields.Float(string='Delivery Qty')

    sale_order_id = fields.Many2one('sale.order',string='Sale Order',readonly=True,)


    @api.multi
    @api.constrains('delivery_qty')
    def check_delivery_qty(self):
        self._check_delivery_qty_validation()


    @api.onchange('delivery_qty')
    def onchange_delivery_qty(self):
        self._check_delivery_qty_validation()

        if self.delivery_qty:
            self.price_subtotal = self.price_unit * self.delivery_qty


    @api.multi
    def write(self, vals):
        if 'delivery_qty' in vals:
            self.price_subtotal = self.price_unit * vals['delivery_qty']

        return super(DeliveryAuthorizationLine, self).write(vals)



    def _check_delivery_qty_validation(self):
        if self.delivery_qty < 0:
            raise ValidationError('Delivery Qty can not be negative')

        da_pool = self.env['delivery.authorization.line'].search([('sale_order_id', '=', self.sale_order_id.id)])
        sum_delivery_qty = 0
        sum_ordered_qty = 0

        if len(da_pool) > 1:

            for da in da_pool:
                sum_delivery_qty += da.delivery_qty
                sum_ordered_qty += da.quantity

            if sum_delivery_qty > sum_ordered_qty:
                raise ValidationError('Delivery Qty can not be greater than Ordered Qty')

        else:
            if self.delivery_qty > self.quantity:
                raise ValidationError('Delivery Qty can not be greater than Ordered Qty')