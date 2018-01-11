from odoo import fields, api, models


class InheritedSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    commission_rate = fields.Float(digits=(16, 2), string="Commission")
    commission_sub_total = fields.Float(string="Total Com.", compute='calculate_commission_subtotal')

    @api.depends('commission_rate', 'product_uom_qty', 'price_subtotal')
    def calculate_commission_subtotal(self):
        for rec in self:
            rec.commission_sub_total = ((rec.commission_rate * rec.price_subtotal) / 100)

    @api.onchange('product_id')
    def onchange_customer(self):
        self.commission_rate = 0
        if self.product_id and self.order_id.partner_id:
            commission = self.env['customer.commission'].search(
                [('customer_id', '=', self.order_id.partner_id.id), ('product_id', '=', self.product_id.id),
                 ('status', '=', True)])

            if commission:
                for coms in commission:
                    if self.order_id.product_id.product_tmpl_id.commission_type == 'fixed':
                        self.commission_rate = coms.commission_rate * self.order_id.order_line.product_uom_qty
                    else:
                        self.commission_rate = coms.commission_rate
            else:
                self.commission_rate = 0

    @api.onchange('product_uom_qty')
    def product_uom_change(self):
        self.commission_rate = 0
        if self.product_id and self.order_id.partner_id:
            commission = self.env['customer.commission'].search(
                [('customer_id', '=', self.order_id.partner_id.id), ('product_id', '=', self.product_id.id),
                 ('status', '=', True)])

            if commission:
                for coms in commission:
                    if self.order_id.product_id.product_tmpl_id.commission_type == 'fixed':
                        self.commission_rate = coms.commission_rate * self.order_id.order_line.product_uom_qty
                    else:
                        self.commission_rate = coms.commission_rate
            else:
                self.commission_rate = 0
