from odoo import models, fields, api

class MRPProductTemplate(models.Model):
    _inherit = "product.template"

    finish_good = fields.Boolean(string='Finish Good', default=False)
    consumable = fields.Boolean('Consumable', default=False)