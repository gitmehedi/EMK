from odoo import api, fields, models, exceptions, _


class SaleTypeProductAccount(models.Model):
    _name = 'sale.type.product.account'


    parent_id = fields.Many2one(comodel_name='product.template', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product',required=True)
    account_id = fields.Many2one('account.account', string='Account', required=True)
    sale_order_type_id = fields.Many2one('sale.order.type', string='Sale Order Type', required=True)
    packing_mode_id = fields.Many2one('product.packaging.mode', string='Packaging Mode')


    # _sql_constraints = [
    #     ('unique_product_id', 'unique(product_id, sale_order_type_id)','Warning!!: This "Product and Sale Order Type" is already in use.'),
    #     ('unique_account_id', 'unique(account_id)','Warning!!: This "Account" is already exists.'),
    # ]


    # @api.onchange('product_id')
    # def _onchange_product_parent_id(self):
    #     domain_id = self.env['product.product'].search([('product_tmpl_id', '=', self.id)]).ids
    #
    #     return {'domain': {'product_id': [('id', 'in', domain_id)]}}


class ProductProduct(models.Model):
    _inherit = 'product.template'

    sale_type_account_ids = fields.One2many('sale.type.product.account', 'parent_id',
                                            string='Sale Product Account')
