from odoo import api, fields, models, _, SUPERUSER_ID
from psycopg2 import IntegrityError
from odoo.exceptions import ValidationError


class TPMManagementModel(models.Model):
    _name = 'tpm.calculation'
    _order = 'code asc'
    _inherit = ['mail.thread']
    _description = 'TPM Management'

    name = fields.Char('Name', required=True, size=200, track_visibility='onchange', readonly=True,
                       states={'draft': [('readonly', False)]})
    code = fields.Char('Code', required=True, size=3, track_visibility='onchange', readonly=True,
                       states={'draft': [('readonly', False)]})
    branch_id = fields.Many2one('operating.unit', string='Branch', readonly=True,
                                states={'draft': [('readonly', False)]}, required=True)
    date = fields.Date(string='Date', default=fields.Date.today, readonly=True,
                       states={'draft': [('readonly', False)]}, required=True)
    line_ids = fields.One2many('tpm.calculation.line', 'line_id', string='Lines', readonly=True,
                               states={'draft': [('readonly', False)]})
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange')

    @api.constrains
    def check_date(self):
        if self.date:
            obj = self.search([()])

    @api.one
    def act_draft(self):
        if self.state == 'reject':
            self.write({
                'state': 'draft',
            })

    @api.one
    def act_approve(self):
        if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
        if self.state == 'draft':
            self.write({
                'state': 'approve',
                'approver_id': self.env.user.id,
            })

    @api.one
    def act_reject(self):
        if self.state == 'draft':
            self.write({
                'state': 'reject',
            })

    @api.one
    def name_get(self):
        name = self.name
        if self.name and self.code:
            name = '[%s] %s' % (self.code, self.name)
        return (self.id, name)

    @api.onchange("name", "code")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()
        if self.code:
            self.code = str(self.code.strip()).upper()

    @api.multi
    def calculate_tpm(self):
        if self.state == 'approve':
            company = self.env.user.company_id
            general_account = company.general_journal_id.id
            income_journal = company.tpm_income_journal_id.id
            expense_journal = company.tpm_expense_journal_id.id
            impact_count = company.impact_count
            impact_unit = company.impact_unit
            income_rate = company.income_rate/100
            expense_rate = company.expense_rate/100
            branch = self.env['operating.unit'].search([('active', '=', True), ('pending', '=', False)])

            query = """SELECT operating_unit_id AS branch,
                            SUM(debit) AS debit,
                            SUM(credit) AS credit,
                            SUM(debit) - SUM(credit) AS balance 
                        FROM account_move_line
                        WHERE account_id=%s AND operating_unit_id IN %s
                        GROUP BY operating_unit_id 
                        ORDER BY operating_unit_id ASC; """ % (general_account, tuple(branch.ids))

            self.env.cr.execute(query)
            for bal in self.env.cr.fetchall():
                branch_id = bal[0]
                journal = 1
                if bal[3] > 0:
                    cr_account = income_journal
                    dr_amount = general_account
                    debit_amount = 0.0
                    credit_amount = round(bal[3] * income_rate, 2)
                    cr_name = 'Income of bank'
                    dr_name = 'General account'
                else:
                    cr_account = general_account
                    dr_amount = expense_journal
                    debit_amount = round(abs(bal[3] * expense_rate), 2)
                    credit_amount = 0.0
                    cr_name = 'General account'
                    dr_name = 'Expense of bank'

                current_currency = self.env.user.company_id.currency_id.id
                credit = {
                    'name': cr_name,
                    'account_id': cr_account,
                    'debit': debit_amount,
                    'credit': credit_amount,
                    'journal_id': journal,
                    'operating_unit_id': branch_id,
                    'currency_id': current_currency,
                    'amount_currency': 0.0,
                }
                debit = {
                    'name': dr_name,
                    'account_id': dr_amount,
                    'credit': debit_amount,
                    'debit': credit_amount,
                    'journal_id': journal,
                    'operating_unit_id': branch_id,
                    'currency_id': current_currency,
                    'amount_currency': 0.0,
                }
                move_list = {
                    'ref': 'Journal ID',
                    'date': fields.Datetime.now(),
                    'journal_id': 1,
                    'is_cr': True,
                    'line_ids': [(0, 0, credit), (0, 0, debit)],
                }

                move = self.env['account.move'].create(move_list)
                tpm_line = {
                    'name': self.id,
                    'journal_id': move.id,
                    'journal_amount': credit_amount if credit_amount > 0 else debit_amount,
                    'branch_id': branch_id,
                    'date': fields.Datetime.now(),
                    'line_id': self.id,
                }

                if move.state == 'draft':
                    move.post()
                    self.line_ids.create(tpm_line)

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'reject'):
                raise ValidationError(_('[Warning] Approves and Rejected record cannot be deleted.'))

            try:
                return super(TPMManagementModel, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))


class TPMManagementLineModel(models.Model):
    _name = 'tpm.calculation.line'
    _order = 'id desc'

    name = fields.Char(string="Name")
    journal_id = fields.Many2one("account.move", string="Journal", required=True)
    journal_amount = fields.Float(string='Journal Amount', digits=(14, 2))
    branch_id = fields.Many2one('operating.unit', string='Branch', required=True)
    date = fields.Date(string='Date', default=fields.Date.today, required=True)
    line_id = fields.Many2one("tpm.calculation", string='Line')
