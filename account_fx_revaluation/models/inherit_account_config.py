from odoo import api, fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    fx_revaluation_journal_id = fields.Many2one('account.journal', string='FX Revaluation Journal', required=True,
                                                help="Account Journal that used when FX Revaluation revaluated")
    fx_revaluation_account_id = fields.Many2one('account.account', string='FX Revaluation Account', required=True,
                                                help="Account for FX Revaluation")

    @api.multi
    def set_fx_revaluation_journal_id(self):
        if self.fx_revaluation_journal_id and self.fx_revaluation_journal_id != self.company_id.fx_revaluation_journal_id:
            self.company_id.write({'fx_revaluation_journal_id': self.fx_revaluation_journal_id.id})
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'fx_revaluation_journal_id', self.fx_revaluation_journal_id.id)

    @api.multi
    def set_fx_revaluation_account_id(self):
        if self.fx_revaluation_account_id and self.fx_revaluation_account_id != self.company_id.fx_revaluation_account_id:
            self.company_id.write({'fx_revaluation_account_id': self.fx_revaluation_account_id.id})
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'fx_revaluation_account_id', self.fx_revaluation_account_id.id)


class ResCompany(models.Model):
    _inherit = "res.company"

    fx_revaluation_journal_id = fields.Many2one('account.journal', string='FX Revaluation Journal',
                                                help="Account Journal that used when FX Revaluation revaluated")
    fx_revaluation_account_id = fields.Many2one('account.account', string='Security Deposit Account',
                                                help="Account for FX Revaluation")
