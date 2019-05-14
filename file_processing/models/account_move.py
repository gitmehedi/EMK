from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_cbs = fields.Boolean(default=False)
