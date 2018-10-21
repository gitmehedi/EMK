# -*- coding: utf-8 -*-
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class ProductCostPriceHistory(models.Model):
    _name = 'product.cost.price.history'
    _order = 'modified_datetime desc'


    current_price = fields.Float('Current Price',digits=dp.get_precision('Product Price'))
    old_price = fields.Float('Old Price',digits=dp.get_precision('Product Price'))
    modified_datetime = fields.Datetime('Modified Date')

    product_id = fields.Many2one('product.product', 'Product', ondelete='cascade', required=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', ondelete='cascade', required=True)
    company_id = fields.Many2one('res.company', 'Company', ondelete='cascade', required=True)
    uom_id = fields.Many2one('product.uom', 'UoM', ondelete='cascade', required=True)


