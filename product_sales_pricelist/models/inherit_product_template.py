from odoo import api, fields, models


class InheritProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def action_view_pricing_history(self):

        view = self.env.ref('product_sales_pricelist.sale_price_change_history_tree')

        return {
            'name': ('Product Price History'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'product.sale.history.line',
            'domain': [('product_id','in', self.product_variant_ids.ids)],
            'context':{'search_default_group_product_id': 1},
            'view_id': [view.id],
            'type': 'ir.actions.act_window'
        }
