from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = "res.company"

    tds_vat_transfer_account_id = fields.Many2one('account.account', string='Transfer Account',
                                                  help="Sundry account used when TDS/VAT challan deposited")
    tds_vat_transfer_journal_id = fields.Many2one('account.journal', string='Transfer Journal',
                                                  help="Account Journal that used when TDS/VAT challan deposited")