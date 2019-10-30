from odoo import api, fields, models, _

class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def _get_default_journal_id(self):
        return self.env.user.company_id.tds_vat_transfer_journal_id

    tds_vat_transfer_journal_id = fields.Many2one('account.journal',string='Transfer Journal',
                                                  default=lambda self: self._get_default_journal_id(),
                                                  help="Account Journal that used when TDS/VAT challan deposited")

    @api.multi
    def set_tds_vat_transfer_journal_id(self):
        if self.tds_vat_transfer_journal_id and self.tds_vat_transfer_journal_id != self.company_id.tds_vat_transfer_journal_id:
            self.company_id.write({'tds_vat_transfer_journal_id': self.tds_vat_transfer_journal_id.id})
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'tds_vat_transfer_journal_id', self.tds_vat_transfer_journal_id.id)