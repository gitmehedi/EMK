from odoo import api, fields, models
from odoo.exceptions import ValidationError


class InheritProductTemplate(models.Model):
    _inherit = 'product.template'

    max_ordering_qty = fields.Float(string='Max Ordering Qty', readonly=True, default=100)
    purchase_ok = fields.Boolean(string='Can be Purchased',default=False)

    # @api.multi
    # def _calculate_available_qty(self):
    #     for prod in self:
    #         ordered_qty_pool = self.env['ordered.qty'].search([('lc_id', '=', False),
    #                                                            ('company_id', '=', prod.company_id.id),
    #                                                            ('product_id', '=', prod.id)])
    #         if not ordered_qty_pool:
    #             prod.available_qty = 100
    #             #return;
    #
    #         for ord_qty in ordered_qty_pool:
    #             if not ord_qty.lc_id:
    #                 prod.available_qty = ord_qty.available_qty
    #             else:
    #                 prod.available_qty = 100

    #available_qty = fields.Float(string='Available Qty', compute='_calculate_available_qty')

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

    @api.constrains('sale_delay')
    def _check_negative_value_sale_delay(self):
        if self.sale_delay < 0.00:
            raise ValidationError('Customer Lead Time can not be negative')
