from odoo import models, fields, api


class SaleTypeProductAccount(models.Model):
    _name = 'sale.type.product.account'

    # product_parent_id = fields.Many2one('product.template', default=lambda self: self.env.context.get('id'))
    #
    # product_id = fields.Many2one('product.product', string='Product', domain="[('product_tmpl_id','=',product_parent_id)]")


    product_parent_id = fields.Many2one('product.template')

    product_id = fields.Many2one('product.product', string='Product')

    account_id = fields.Many2one('account.account', string='Account', required=True)
    sale_order_type_id = fields.Many2one('sale.order.type', string='Sale Order Type', required=True)

    @api.onchange('product_id')
    def _onchange_product_parent_id(self):
        domain_id = self.env['product.product'].search([('product_tmpl_id', '=', 9)]).ids

        return {'domain': {'product_id': [('id', 'in', domain_id)]}}


class ProductProduct(models.Model):
    _inherit = 'product.template'

    sale_type_account_ids = fields.One2many('sale.type.product.account', 'product_parent_id',
                                            string='Sale Product Account')


