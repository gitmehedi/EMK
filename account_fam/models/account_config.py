from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    fa_journal_id = fields.Many2one('account.journal', string='Fixed Asset Journal', required=True)


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    fa_journal_id = fields.Many2one('account.journal', string='Journal', required=True)

    @api.multi
    def set_fa_journal_id(self):
        if self.fa_journal_id:
            self.company_id.write({'fa_journal_id': self.fa_journal_id.id})
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'fa_journal_id', self.fa_journal_id.id)
