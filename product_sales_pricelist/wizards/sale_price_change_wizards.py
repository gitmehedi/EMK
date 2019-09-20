from odoo import api, models, fields


class SalePriceChangeWizards(models.TransientModel):
    _name = 'sale.price.details'

    product_id = fields.Many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], required=True)
    currency_id = fields.Many2one('res.currency', string="Currency")

    @api.multi
    def search_data(self):
        view = self.env.ref('product_sales_pricelist.sale_price_change_tree')
        pricelist_pool = self.env['product.sales.pricelist']

        if self.product_id and self.currency_id:
            pricelist_obj = pricelist_pool.search([('state','=','validate'),('product_id', '=', self.product_id.id),('currency_id', '=', self.currency_id.id)])

            return {
                'name': ('Price History'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'product.sales.pricelist',
                'domain': [('id', '=', pricelist_obj.ids)],
                'view_id': [view.id],
                'type': 'ir.actions.act_window'
            }
        elif self.product_id:
            pricelist_obs = pricelist_pool.search([('state','=','validate'),('product_id', '=', self.product_id.id)])

            return {
                'name': ('Price History'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'product.sales.pricelist',
                'domain': [('id', '=', pricelist_obs.ids)],
                'view_id': [view.id],
                'type': 'ir.actions.act_window'
            }
