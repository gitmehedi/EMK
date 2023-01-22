from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    advance_id = fields.Many2one('vendor.advance', copy=False, string='VA/RA')