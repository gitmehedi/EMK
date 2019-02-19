from odoo import api, fields, models, _

class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def _get_default_account_id(self):
        return self.env['account.account'].search([('user_type_id', '=', self.env.ref('account.data_account_type_expenses').id)], limit=1)

    def _get_default_journal_id(self):
        return self.env['account.journal'].search([('type', '=', 'general')], limit=1)


    tds_vat_transfer_account_id = fields.Many2one('account.account',string='Transfer Account',required=True,
                                                  default=lambda self: self._get_default_account_id(),
                                                  help="Sundry account used when TDS/VAT challan deposited")
    tds_vat_transfer_journal_id = fields.Many2one('account.journal',string='Transfer Journal',required=True,
                                                  default=_get_default_journal_id,
                                                  help="Account Journal that used when TDS/VAT challan deposited")

    @api.multi
    def set_loan_approve(self):
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'tds_vat_transfer_account_id', self.tds_vat_transfer_account_id)
