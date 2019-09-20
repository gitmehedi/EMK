from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_confirm(self):

        for order in self:
            order.state = 'sale'
            order.confirmation_date = fields.Datetime.now()
            if self.env.context.get('send_email'):
                self.force_quotation_send()

            sales_setting_pool = self.env['sale.config.settings'].search([], order='id desc', limit=1)

            if sales_setting_pool:
                if sales_setting_pool.delivery_order_auto_generate:
                    order.order_line._action_procurement_create()

        if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
            self.action_done()
        return True
