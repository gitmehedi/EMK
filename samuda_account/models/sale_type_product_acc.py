from odoo import models, fields, api

class SaleTypeProductAccount(models.Model):
    _name = 'sale.type.product.account'


    product_id = fields.Many2one('product.product', string='Product',required=True)
    account_id = fields.Many2one('account.account', string='Account', required=True)
    sale_order_type_id = fields.Many2one('sale.order.type',string='Sale Order Type',required=True)
    product_parent_id = fields.Many2one('product.template')


class ProductProduct(models.Model):
    _inherit = 'product.template'

    sale_type_account_ids = fields.One2many('sale.type.product.account','product_parent_id',string='Sale Product Account')