from odoo import fields, models


class ProductIncomeAccountConfiguration(models.Model):
    _name = 'product.income.acc.conf'

    so_type_id = fields.Many2one('sale.order.type', string='Sale Order Type')
    currency_id = fields.Many2one('res.currency', string='Currency')
    sale_local_foreign = fields.Selection([('local', 'Local'), ('foreign', 'Foreign')], 'Local/Foreign Sale')

    account_id = fields.Many2one('account.account', string='Product Income Account')

    parent_id = fields.Many2one('product.product', ondelete='cascade')
