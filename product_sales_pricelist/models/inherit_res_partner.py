from odoo import api, fields, models
from odoo.exceptions import ValidationError


class InheritResPartner(models.Model):
    _inherit = 'res.partner'
