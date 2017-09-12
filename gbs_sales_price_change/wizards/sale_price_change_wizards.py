from odoo import api, models, fields


class SalePriceChangeWizards(models.TransientModel):
    _name = 'sale.price.details'

    product_id = fields.Many2one('product.product', 'Product', required=True)
    currency_id = fields.Many2one('res.currency', string="Currency")

    @api.multi
    def search_data(self):
        view = self.env.ref('gbs_sales_price_change.sale_price_change_tree')
        employee_pool = self.env['sale.price.change']

        if self.product_id:
            emp_ids = employee_pool.search([('product_id', '=', self.product_id.id),('currency_id', '=', self.currency_id.id)])

            return {
                'name': ('Price History'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'sale.price.change',
                'domain': [('id', '=', emp_ids.ids)],
                'view_id': [view.id],
                'type': 'ir.actions.act_window'
            }
