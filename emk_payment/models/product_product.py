from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = 'product.template'

    service_type = fields.Selection([('card', 'Card'), ('copy', 'Copy')])
