from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    commission_refund_account_payable_id = fields.Many2one(
        comodel_name='account.account',
        string='Account Payable for Commission and Refund'
    )
