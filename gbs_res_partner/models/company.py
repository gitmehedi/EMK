from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = "res.company"

    sundry_account_id = fields.Many2one('account.account', string='Sundry Account',
                                        help="Sundry account used to Vendor bill payment instruction")