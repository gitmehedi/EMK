from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    general_journal_id = fields.Many2one('account.account', string='General Journal', required=True)
    tpm_income_journal_id = fields.Many2one('account.account', string='Income Journal', required=True)
    tpm_expense_journal_id = fields.Many2one('account.account', string='Expense Journal', required=True)
    impact_count = fields.Integer(string='Expense Journal', required=True)
    impact_unit = fields.Selection([('days', 'Days'), ('month', 'Month')], required=True)


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def _get_default_general_journal_id(self):
        return self.env.user.company_id.general_journal_id

    def _get_default_tpm_income_journal_id(self):
        return self.env.user.company_id.tpm_income_journal_id

    def _get_default_tpm_expense_journal_id(self):
        return self.env.user.company_id.tpm_expense_journal_id

    def _get_default_impact_count(self):
        return self.env.user.company_id.impact_count

    def _get_default_impact_unit(self):
        return self.env.user.company_id.impact_unit

    general_journal_id = fields.Many2one('account.account', string='Retain Earnings', required=True,
                                         default=lambda self: self._get_default_general_journal_id(),
                                         domain="[('level_id.name','=','Layer 5')]")
    tpm_income_journal_id = fields.Many2one('account.account', string='Retain Earnings', required=True,
                                            default=lambda self: self._get_default_tpm_income_journal_id(),
                                            domain="[('level_id.name','=','Layer 5')]")
    tpm_expense_journal_id = fields.Many2one('account.account', string='General Account', required=True,
                                             default=lambda self: self._get_default_tpm_expense_journal_id(),
                                             domain="[('level_id.name','=','Layer 5')]")
    impact_count = fields.Integer(string='Expense Journal', default=1, required=True)
    impact_unit = fields.Selection([('days', 'Days'), ('month', 'Month')], default='days', required=True)

    @api.multi
    def set_general_journal_id(self):
        if self.general_journal_id:
            self.company_id.write({'general_journal_id': self.general_journal_id.id})
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'general_journal_id',
                                                        self.general_journal_id.id)

    @api.multi
    def set_tpm_income_journal_id(self):
        if self.tpm_income_journal_id:
            self.company_id.write({'tpm_income_journal_id': self.tpm_income_journal_id.id})
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'tpm_income_journal_id',
                                                        self.tpm_income_journal_id.id)

    @api.multi
    def set_tpm_expense_journal_id(self):
        if self.tpm_expense_journal_id:
            self.company_id.write({'tpm_expense_journal_id': self.tpm_expense_journal_id.id})
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'tpm_expense_journal_id',
                                                        self.tpm_expense_journal_id.id)

    @api.multi
    def set_impact_count(self):
        if self.impact_count:
            self.company_id.write({'impact_count': self.impact_count})
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'impact_count', self.impact_count)

    @api.multi
    def set_impact_unit(self):
        if self.impact_unit:
            self.company_id.write({'impact_unit': self.impact_unit})
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'impact_unit', self.impact_unit)
