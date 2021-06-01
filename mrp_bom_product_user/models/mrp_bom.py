from odoo import api, fields, models, _


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    product_tmpl_id = fields.Many2one('product.template',
                                      domain="[('manufacture_ok', '=', True), ('type', 'in', ['product', 'consu'])]")
