from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_cbs = fields.Boolean(default=False, help='CBS data always sync with OGL using GLIF.')
    is_sync = fields.Boolean(default=False, help='OGL continuously send data to CBS for journal sync.')
