from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    journal_id = fields.Many2one('account.journal', string='TPM Journal', required=True)
    tpm_general_account_id = fields.Many2one('account.account', string='General Journal', required=True)
    tpm_general_seq_id = fields.Many2one('sub.operating.unit', string='General Journal Sequence', required=True)
    tpm_income_account_id = fields.Many2one('account.account', string='Income Journal', required=True)
    tpm_income_seq_id = fields.Many2one('sub.operating.unit', string='Income Journal Sequence', required=True)
    tpm_expense_account_id = fields.Many2one('account.account', string='Expense Journal', required=True)
    tpm_expense_seq_id = fields.Many2one('sub.operating.unit', string='Expense Journal Sequence', required=True)
    impact_count = fields.Integer(string='Expense Journal', required=True)
    impact_unit = fields.Selection([('days', 'Days'), ('month', 'Month')], required=True)
    impact_unit = fields.Selection([('days', 'Days'), ('month', 'Month')], required=True)
    income_rate = fields.Float(string='Income Rate', required=True)
    expense_rate = fields.Float(string='Expense Rate', required=True)
    days_in_fy = fields.Integer(string='Days in Year', size=3, required=True)


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def _get_default_journal_id(self):
        return self.env.user.company_id.journal_id

    def _get_default_tpm_general_account_id(self):
        return self.env.user.company_id.tpm_general_account_id

    def _get_default_tpm_general_seq_id(self):
        return self.env.user.company_id.tpm_general_seq_id

    def _get_default_tpm_income_account_id(self):
        return self.env.user.company_id.tpm_income_account_id

    def _get_default_tpm_income_seq_id(self):
        return self.env.user.company_id.tpm_income_seq_id

    def _get_default_tpm_expense_account_id(self):
        return self.env.user.company_id.tpm_expense_account_id

    def _get_default_tpm_expense_seq_id(self):
        return self.env.user.company_id.tpm_expense_seq_id

    def _get_default_impact_count(self):
        return self.env.user.company_id.impact_count

    def _get_default_impact_unit(self):
        return self.env.user.company_id.impact_unit

    journal_id = fields.Many2one('account.journal', string='TPM Journal', required=True,
                                 default=lambda self: self._get_default_journal_id())

    tpm_general_account_id = fields.Many2one('account.account', string='General Account', required=True,
                                             default=lambda self: self._get_default_tpm_general_account_id(),
                                             domain="[('level_id.name','=','Layer 5')]")
    tpm_general_seq_id = fields.Many2one('sub.operating.unit', string='General Account Sequence', required=True,
                                         default=lambda self: self._get_default_tpm_general_seq_id())

    tpm_income_account_id = fields.Many2one('account.account', string='Income Account', required=True,
                                            default=lambda self: self._get_default_tpm_income_account_id(),
                                            domain="[('level_id.name','=','Layer 5')]")
    tpm_income_seq_id = fields.Many2one('sub.operating.unit', string='Income Account Sequence', required=True,
                                         default=lambda self: self._get_default_tpm_income_seq_id())

    tpm_expense_account_id = fields.Many2one('account.account', string='Expense Account', required=True,
                                             default=lambda self: self._get_default_tpm_expense_account_id(),
                                             domain="[('level_id.name','=','Layer 5')]")

    tpm_expense_seq_id = fields.Many2one('sub.operating.unit', string='Expense Account Sequence', required=True,
                                             default=lambda self: self._get_default_tpm_expense_seq_id())

    impact_count = fields.Integer(string='Expense Journal', default=1, required=True)
    impact_unit = fields.Selection([('days', 'Days'), ('month', 'Month')], default='days', required=True)
    income_rate = fields.Float(string='Income Rate', required=True)
    expense_rate = fields.Float(string='Expense Rate', required=True)
    days_in_fy = fields.Integer(string='Days in Year', size=3, required=True, default=360)

    @api.multi
    def set_journal_id(self):
        if self.journal_id:
            self.company_id.write({'journal_id': self.journal_id.id})
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'journal_id',
                                                        self.journal_id.id)

    @api.multi
    def set_tpm_general_account_id(self):
        if self.tpm_general_account_id:
            self.company_id.write({'tpm_general_account_id': self.tpm_general_account_id.id})
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'tpm_general_account_id',
                                                        self.tpm_general_account_id.id)
    @api.multi
    def set_tpm_general_seq_id(self):
        if self.tpm_general_seq_id:
            self.company_id.write({'tpm_general_seq_id': self.tpm_general_seq_id.id})
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'tpm_general_seq_id',
                                                        self.tpm_general_seq_id.id)

    @api.multi
    def set_tpm_income_account_id(self):
        if self.tpm_income_account_id:
            self.company_id.write({'tpm_income_account_id': self.tpm_income_account_id.id})
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'tpm_income_account_id',
                                                        self.tpm_income_account_id.id)
    @api.multi
    def set_tpm_income_seq_id(self):
        if self.tpm_income_seq_id:
            self.company_id.write({'tpm_income_seq_id': self.tpm_income_seq_id.id})
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'tpm_income_seq_id',
                                                        self.tpm_income_seq_id.id)

    @api.multi
    def set_tpm_expense_account_id(self):
        if self.tpm_expense_account_id:
            self.company_id.write({'tpm_expense_account_id': self.tpm_expense_account_id.id})
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'tpm_expense_account_id',
                                                        self.tpm_expense_account_id.id)

    @api.multi
    def set_tpm_expense_seq_id(self):
        if self.tpm_expense_seq_id:
            self.company_id.write({'tpm_expense_seq_id': self.tpm_expense_seq_id.id})
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'tpm_expense_seq_id',
                                                        self.tpm_expense_seq_id.id)

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

    @api.multi
    def set_income_rate(self):
        if self.income_rate:
            self.company_id.write({'income_rate': self.income_rate})
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'income_rate', self.income_rate)

    @api.multi
    def set_expense_rate(self):
        if self.expense_rate:
            self.company_id.write({'expense_rate': self.expense_rate})
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'expense_rate', self.expense_rate)

    @api.multi
    def set_days_in_fy(self):
        if self.days_in_fy:
            self.company_id.write({'days_in_fy': self.days_in_fy})
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'days_in_fy', self.days_in_fy)
