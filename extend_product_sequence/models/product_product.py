from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    default_code = fields.Char(string="Internal Reference", required=False)
