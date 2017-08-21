from odoo import fields, api, models


class InheritedSaleOrder(models.Model):
    _inherit='sale.order'

    commission_total = fields.Float(string="Commission Total", compute='calculate_commission_total')


    @api.depends('order_line.commission_rate')
    def calculate_commission_total(self):
        for rec in self:
            return True

class InheritedSaleOrderLine(models.Model):
    _inherit='sale.order.line'


    commission_rate = fields.Float(string="Commission Rate")
    commission_sub_total = fields.Float(string="Commission Sub Total", compute='calculate_commission_subtotal')


    @api.depends('commission_rate')
    def calculate_commission_subtotal(self):
        for rec in self:
            return True


    @api.onchange('product_id')
    def onchange_customer(self):
        self.commission_rate = 0
        if self.product_id and self.order_id.customer_id:
            commission = self.env['customer.commission'].search(
                [('customer_id', '=', self.order_id.customer_id.id), ('product_id', '=', self.product_id.id),
                 ('status', '=', True)])

            self.commission_rate = commission.commission_rate if commission else 0