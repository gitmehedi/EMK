from odoo import api, fields, models, tools, _


class ProductCategory(models.Model):
    _name = "product.template"
    _inherit = ['product.template']


    name = fields.Char('Name', index=True, required=True,track_visibility='onchange', translate=True)
    type = fields.Selection(track_visibility='onchange')

    categ_id = fields.Many2one(track_visibility='onchange')
    list_price = fields.Float(track_visibility='onchange')
    hs_code = fields.Char(track_visibility='onchange')
    hs_code_id = fields.Many2one(track_visibility='onchange')
    origin_country_id = fields.Many2one(track_visibility='onchange')
    company_id = fields.Many2one(track_visibility='onchange')
    uom_id = fields.Many2one(track_visibility='onchange')
    default_code = fields.Char(track_visibility='onchange')
    attribute_line_ids = fields.One2many('product.attribute.line', 'product_tmpl_id', 'Product Attributes',track_visibility='onchange')

    commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed')
    ], string='Commission Type', default='percentage',track_visibility='onchange')
    property_account_income_id = fields.Many2one(track_visibility='onchange')
    property_account_expense_id = fields.Many2one(track_visibility='onchange')

