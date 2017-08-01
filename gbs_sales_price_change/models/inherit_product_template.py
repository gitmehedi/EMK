from odoo import api, fields, models


class InheritProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def action_view_pricing_history(self):

        view = self.env.ref('gbs_sales_price_change.sale_price_change_history_tree')

        return {
            'name': ('Product Price History'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'product.sale.history.line',
            'domain': [('product_id','=',self.id)],
            'view_id': [view.id],
            'type': 'ir.actions.act_window'
        }
