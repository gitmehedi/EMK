# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductVariantHistory(models.Model):
    _name = 'product.variant.history'

    product_id = fields.Many2one('product.product', 'Product', ondelete='cascade', required=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template Id', ondelete='cascade', required=True)
    company_id = fields.Many2one('res.company', 'Company',ondelete='cascade')
    product_unit_id = fields.Many2one('product.category', 'Internal Category', ondelete='cascade')
    value = fields.Float('Value')
    effective_datetime = fields.Datetime('Effective Date')