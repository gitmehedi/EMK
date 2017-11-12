from odoo import api, fields, models


class InheritProductTemplate(models.Model):
    _inherit = 'product.template'
    max_ordering_qty = fields.Float(string='Max Ordering Qty.', default=100, required=True)
    purchase_ok = fields.Boolean(string='Can be Purchased',default=False)


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

    @api.constrains('name')
    def _check_unique_constraint(self):
        if self.name:
            filters = [['name', '=ilike', self.name]]
            name = self.search(filters)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')
