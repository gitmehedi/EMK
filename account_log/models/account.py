from odoo import models, fields, api, _


class AccountAccount(models.Model):
    _name = "account.account"
    _inherit = ["account.account", "mail.thread"]

    name = fields.Char(required=True, index=True, track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string='Account Currency', track_visibility='onchange',
                                  help="Forces all moves for this account to have this account currency.")
    code = fields.Char(size=64, required=True, index=True, track_visibility='onchange')
    deprecated = fields.Boolean(index=True, default=False, track_visibility='onchange')
    user_type_id = fields.Many2one('account.account.type', string='Type', required=True, oldname="user_type", track_visibility='onchange',
                                   help="Account Type is used for information purpose, to generate country-specific legal reports, and set the rules to close a fiscal year and generate opening entries.")

    reconcile = fields.Boolean(string='Allow Reconciliation', default=False, track_visibility='onchange',
                               help="Check this box if this account allows invoices & payments matching of journal items.")

    company_id = fields.Many2one('res.company', string='Company', required=True, track_visibility='onchange',
                                 default=lambda self: self.env['res.company']._company_default_get('account.account'))

    parent_id = fields.Many2one('account.account', 'Parent Account', ondelete="set null", track_visibility='onchange')

    type_third_parties = fields.Selection([('no', 'No'), ('supplier', 'Supplier'), ('customer', 'Customer')],
                                          string='Third Partie', required=True, default='no', track_visibility='onchange')
