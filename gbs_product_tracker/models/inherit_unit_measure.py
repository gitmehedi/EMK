from odoo import api, fields, models, tools, _


class ProductCategory(models.Model):
    _name = "product.uom"
    _inherit = ['product.uom', 'mail.thread']

    name = fields.Char('Unit of Measure', required=True, translate=True,track_visibility='onchange')
    category_id = fields.Many2one(
        'product.uom.categ', 'Category', required=True, ondelete='cascade', track_visibility='onchange',
        help="Conversion between Units of Measure can only occur if they belong to the same category. The conversion will be made based on the ratios.")

    active = fields.Boolean('Active', default=True, track_visibility='onchange',
                            help="Uncheck the active field to disable a unit of measure without deleting it.")
    uom_type = fields.Selection([
        ('bigger', 'Bigger than the reference Unit of Measure'),
        ('reference', 'Reference Unit of Measure for this category'),
        ('smaller', 'Smaller than the reference Unit of Measure')], 'Type',
        default='reference', required=1,track_visibility='onchange')