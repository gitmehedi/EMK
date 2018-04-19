from odoo import models, fields, api

class MRPProductTemplate(models.Model):
    _inherit = "product.template"

    finish_good = fields.Boolean('Finish Good', default=True)
    consumable = fields.Boolean('Consumable', default=True)