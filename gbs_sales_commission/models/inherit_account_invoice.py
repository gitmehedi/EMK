from odoo import api, fields, models


class InheritAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    is_commission_generated = fields.Boolean(string='Commission Generated', default=False)
    generated_commission_amount = fields.Float(string='Commission Amount', compute="_calculate_commission_amount")

    @api.multi
    def _calculate_commission_amount(self):
        sale_order_pool = self.env['sale.order'].search([('name', '=', self.origin)])

        sum_com = 0
        commission = None
        for sale_line in sale_order_pool.order_line:
            commission_type = sale_line.product_id.product_tmpl_id.commission_type

            if commission_type == 'fixed':
                if sale_line.product_uom_qty == self.invoice_line_ids.quantity:
                    commission = sale_line.commission_rate
                else:
                    commission = sale_line.commission_rate / self.invoice_line_ids.quantity

            elif commission_type == 'percentage':
                if sale_line.product_uom_qty == self.invoice_line_ids.quantity:
                    commission = (sale_line.commission_rate * sale_line.price_subtotal) / 100
                else:
                    commission = ((sale_line.commission_rate * sale_line.price_subtotal) / 100) / self.invoice_line_ids.quantity

            self.generated_commission_amount = commission
