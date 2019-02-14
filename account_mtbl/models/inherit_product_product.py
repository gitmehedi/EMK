from odoo import models, fields, api, _

class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = ['product.product','mail.thread']

    name = fields.Char(track_visibility='onchange')
    parent_id = fields.Many2one(track_visibility='onchange')
    #categ_id = fields.Many2one(track_visibility='onchange')
    # type = fields.Selection(track_visibility='onchange')
    default_code = fields.Char(track_visibility='onchange')
    barcode = fields.Char(track_visibility='onchange')
    lst_price = fields.Float(track_visibility='onchange')
    standard_price = fields.Float(track_visibility='onchange')
    account_tds_id = fields.Many2one(track_visibility='onchange')