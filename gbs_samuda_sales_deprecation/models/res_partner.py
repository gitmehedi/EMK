# imports of odoo
from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_deprecated = fields.Boolean(string="Deprecated")
