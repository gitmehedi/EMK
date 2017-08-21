from odoo import fields, api, models


class InheritedSaleOrder(models.Model):
    _inherit = 'sale.order'

    commission_total = fields.Float(string="Commission Total", compute='calculate_commission_total')

    @api.depends('order_line.commission_rate','order_line.product_uom_qty')
    def calculate_commission_total(self):
        for record in self:
            sum = 0
            for rec in record.order_line:
                sum = sum + (rec.commission_rate * rec.product_uom_qty)

            record.commission_total = sum


class InheritedSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    commission_rate = fields.Float(string="Com. Rate")
    commission_sub_total = fields.Float(string="Com. Subtotal", compute='calculate_commission_subtotal')

    @api.depends('commission_rate','product_uom_qty')
    def calculate_commission_subtotal(self):
        for rec in self:
            rec.commission_sub_total = rec.commission_rate * rec.product_uom_qty

    @api.onchange('product_id')
    def onchange_customer(self):
        self.commission_rate = 0
        if self.product_id and self.order_id.partner_id:
            commission = self.env['customer.commission'].search(
                [('customer_id', '=', self.order_id.partner_id.id), ('product_id', '=', self.product_id.id),
                 ('status', '=', True)])

            self.commission_rate = commission.commission_rate if commission else 0
