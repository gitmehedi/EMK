from datetime import datetime, timedelta
from odoo import api, fields, models, _, SUPERUSER_ID
from psycopg2 import IntegrityError
from odoo.exceptions import ValidationError,Warning


class TPMManagementModel(models.Model):
    _name = 'tpm.calculation'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'TPM Management'
    _order = 'id desc'

    def _default_from_date(self):
        date = self.search([('state', '=', 'confirm')], order='to_date desc', limit=1)

        if date:
            next = datetime.strptime(date.to_date, "%Y-%m-%d") + timedelta(days=+1)
            return next.strftime("%Y-%m-%d")
        else:
            return fields.Date.today()

    name = fields.Char('Name', size=200, track_visibility='onchange', readonly=True)
    branch_id = fields.Many2one('operating.unit', string='Branch', readonly=True,
                                states={'draft': [('readonly', False)]}, required=True)
    date = fields.Date(string='From Date', default=_default_from_date, required=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    to_date = fields.Date(string='To Date', required=True, readonly=True,
                          states={'draft': [('readonly', False)]})
    total_income = fields.Float(string="Total Income", compute="_compute_income_expense")
    total_expense = fields.Float(string="Total Expense", compute="_compute_income_expense")
    balance = fields.Float(string="Difference", compute="_compute_income_expense")
    journal_id = fields.Many2one('account.move', string='Journal Entry', readonly=True)
    line_ids = fields.One2many('tpm.calculation.line', 'line_id', string='Lines', readonly=True)
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'),
                              ('calculate', 'Calculate'),
                              ('confirm', 'Confirmed'),
                              ('approve', 'Approved'),
                              ('reject', 'Rejected')],
                             default='draft', string='Status', track_visibility='onchange')

    @api.constrains("date", "to_date")
    def check_date(self):
        # date = self._default_from_date()
        # if date != self.date:
        #     raise ValidationError(_("From Date value in not appropriate."))
        if self.date > self.to_date:
            raise ValidationError(_("From Date should not be greater than To Date."))

    @api.multi
    @api.depends('line_ids')
    def _compute_income_expense(self):
        for rec in self:
            rec.total_income = sum([val.income for val in rec.line_ids])
            rec.total_expense = sum([val.expense for val in rec.line_ids])
            rec.balance = abs(rec.total_income - rec.total_expense)

    @api.one
    def act_draft(self):
        if self.state == 'calculate':
            self.write({
                'state': 'draft',
            })

    @api.multi
    def calculate_tpm(self):
        if self.state == 'draft':
            self.line_ids.unlink()

            company = self.env.user.company_id
            days = company.days_in_fy
            general_account = company.tpm_general_account_id.id
            income_rate = (company.income_rate / 100) / days
            expense_rate = (company.expense_rate / 100) / days
            branch = self.env['operating.unit'].search([('active', '=', True), ('pending', '=', False)])
            branch_lines = {}
            for val in branch:
                branch_lines[val.id] = []

            cur_date = fields.Date.today()
            fy = self.env['date.range'].search([('date_end', '>=', cur_date), ('date_start', '<=', cur_date),
                                                ('type_id.fiscal_year', '=', True), ('active', '=', True)])
            if not fy:
                raise Warning(_("Financial is not available. Please create current financial year."))

            fy_start_date = fy.date_start
            d1 = datetime.strptime(self.date, "%Y-%m-%d")
            d2 = datetime.strptime(self.to_date, "%Y-%m-%d")
            no_of_days = (d2 - d1).days + 1
            for day in range(0, no_of_days):
                start_date = d1 + timedelta(days=day)
                end_date = d1 + timedelta(days=day)

                query = """SELECT aa.id,
                                   COALESCE(trial.credit, 0) AS credit,
                                   COALESCE(trial.debit, 0) AS debit,
                                   (COALESCE(trial.credit, 0) - COALESCE(trial.debit, 0) + COALESCE(init.balance, 0)) AS balance,
                                   COALESCE(init.balance, 0) AS init_bal
                            FROM operating_unit aa
                            LEFT JOIN (SELECT aml.operating_unit_id AS id,
                                              COALESCE(SUM(aml.debit), 0) AS debit,
                                              COALESCE(SUM(aml.credit), 0) AS credit
                                        FROM account_move_line aml
                                        LEFT JOIN account_move am
                                           ON (am.id = aml.move_id)
                                        WHERE aml.account_id=%s
                                              AND am.is_cbs=TRUE
                                              AND (aml.date >= '%s'
                                              AND aml.date <= '%s') 
                                        GROUP  BY aml.operating_unit_id) trial ON (trial.id = aa.id)
                            LEFT JOIN (SELECT aml.operating_unit_id AS id,
                                              COALESCE((SUM(aml.credit) - SUM(aml.debit)), 0) AS balance
                                        FROM account_move_line aml
                                        LEFT JOIN account_move am
                                           ON (am.id = aml.move_id)
                                        WHERE aml.account_id=%s
                                              AND am.is_cbs=TRUE
                                              AND (aml.date >= '%s'
                                              AND aml.date < '%s')
                                        GROUP  BY aml.operating_unit_id) init ON (init.id = aa.id)
                            WHERE aa.active=True 
                                  AND aa.pending=False
                            ORDER BY aa.id ASC""" % (
                general_account, start_date, end_date, general_account, fy_start_date, end_date)

                self.env.cr.execute(query)
                for bal in self.env.cr.fetchall():
                    branch_id = bal[0]
                    if branch_id == self.branch_id.id:
                        continue

                    if bal[3] > 0:
                        debit_amount = round(abs(bal[3] * expense_rate), 2)
                        credit_amount = 0.0
                    else:
                        debit_amount = 0.0
                        credit_amount = round(abs(bal[3]) * income_rate, 2)

                    line = {
                        'income': credit_amount,
                        'expense': debit_amount,
                        'balance': bal[3],
                        'pl_status': 'expense' if bal[3] > 0 else 'income',
                        'branch_id': branch_id,
                        'date': start_date,
                        'income_rate': company.income_rate,
                        'expense_rate': company.expense_rate,
                        'branch_line_id': 0,
                    }
                    branch_lines[bal[0]].append(line)

            for key, value in branch_lines.items():
                if key == self.branch_id.id:
                    continue
                line = self.line_ids.create({
                    'name': self.id,
                    'branch_id': key,
                    'from_date': self.date,
                    'to_date': self.to_date,
                    'line_id': self.id,
                })
                for val in value:
                    val['branch_line_id'] = line.id
                    line.branch_line_ids.create(val)

            self.write({'state': 'calculate'})

    @api.multi
    def act_confirm(self):
        if self.state == 'calculate':
            name = self.env['ir.sequence'].next_by_code('tpm.calculation') or ''
            self.write({
                'name': name,
                'state': 'confirm',
                'maker_id': self.env.user.id,
            })


    @api.multi
    def act_approve(self):
        if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
        if self.state == 'confirm':
            lines = []
            date = fields.Datetime.now()
            journal_entry = ""
            company = self.env.user.company_id
            journal = company.journal_id.id
            current_currency = company.currency_id.id
            general_account = company.tpm_general_account_id.id
            income_account = company.tpm_income_account_id.id
            expense_account = company.tpm_expense_account_id.id
            move = self.env['account.move'].create({
                'ref': 'TPM in [{0}] with ref {1}'.format(self.date, self.name),
                'date': date,
                'journal_id': journal,
                'operating_unit_id': self.branch_id.id,
                'is_cr': True,
            })
            for rec in self.line_ids:
                name = "%s for branch %s" % (rec.pl_status.capitalize(), rec.branch_id.display_name.replace("'", ""))
                if rec.income == 0 and rec.expense == 0:
                    continue

                if rec.income > 0:
                    credit_account_id = income_account
                    debit_account_id = general_account
                    income_cr_cr = rec.income
                    income_cr_dr = 0
                    income_dr_cr = 0
                    income_dr_dr = rec.income
                else:
                    credit_account_id = general_account
                    debit_account_id = expense_account
                    income_cr_cr = rec.expense
                    income_cr_dr = 0
                    income_dr_cr = 0
                    income_dr_dr = rec.expense

                credit = {
                    'name': name,
                    'date': date,
                    'date_maturity': date,
                    'account_id': credit_account_id,
                    'credit': income_cr_cr,
                    'debit': income_cr_dr,
                    'journal_id': journal,
                    'operating_unit_id': rec.branch_id.id,
                    'currency_id': current_currency,
                    'amount_currency': 0.0,
                    'move_id': move.id,
                    'company_id': company.id,
                }
                debit = {
                    'name': name,
                    'date': date,
                    'date_maturity': date,
                    'account_id': debit_account_id,
                    'credit': income_dr_cr,
                    'debit': income_dr_dr,
                    'journal_id': journal,
                    'operating_unit_id': rec.branch_id.id,
                    'currency_id': current_currency,
                    'amount_currency': 0.0,
                    'move_id': move.id,
                    'company_id': company.id,
                }
                journal_entry += self.format_journal(credit)
                journal_entry += self.format_journal(debit)

            if self.total_expense:
                name = "Income of %s" % (self.branch_id.display_name.replace("'", ""))

                inc_credit = {
                    'name': name,
                    'date': date,
                    'date_maturity': date,
                    'account_id': income_account,
                    'credit': self.total_expense,
                    'debit': 0,
                    'journal_id': journal,
                    'operating_unit_id': self.branch_id.id,
                    'currency_id': current_currency,
                    'amount_currency': 0.0,
                    'move_id': move.id,
                    'company_id': company.id,
                }
                inc_debit = {
                    'name': name,
                    'date': date,
                    'date_maturity': date,
                    'account_id': general_account,
                    'credit': 0,
                    'debit': self.total_expense,
                    'journal_id': journal,
                    'operating_unit_id': self.branch_id.id,
                    'currency_id': current_currency,
                    'amount_currency': 0.0,
                    'move_id': move.id,
                    'company_id': company.id,
                }
                journal_entry += self.format_journal(inc_credit)
                journal_entry += self.format_journal(inc_debit)

            if self.total_income:
                name = "Expense of %s" % (self.branch_id.display_name.replace("'", ""))

                exp_credit = {
                    'name': name,
                    'date': date,
                    'date_maturity': date,
                    'account_id': general_account,
                    'credit': self.total_income,
                    'debit': 0,
                    'journal_id': journal,
                    'operating_unit_id': self.branch_id.id,
                    'currency_id': current_currency,
                    'amount_currency': 0.0,
                    'move_id': move.id,
                    'company_id': company.id,
                }
                exp_debit = {
                    'name': name,
                    'date': date,
                    'date_maturity': date,
                    'account_id': expense_account,
                    'credit': 0,
                    'debit': self.total_income,
                    'journal_id': journal,
                    'operating_unit_id': self.branch_id.id,
                    'currency_id': current_currency,
                    'amount_currency': 0.0,
                    'move_id': move.id,
                    'company_id': company.id,
                }
                journal_entry += self.format_journal(exp_credit)
                journal_entry += self.format_journal(exp_debit)

            query = """INSERT INTO account_move_line 
                                    (move_id, date,date_maturity, operating_unit_id, account_id, name,ref, currency_id, journal_id,
                                    credit,debit,amount_currency,company_id)  
                                    VALUES %s""" % journal_entry[:-1]
            self.env.cr.execute(query)

            if move.state == 'draft':
                move.sudo().post()

            self.write({
                'state': 'approve',
                'approver_id': self.env.user.id,
                'journal_id': move.id,
            })

    @api.one
    def act_reject(self):
        if self.state == 'draft':
            self.write({
                'state': 'reject',
            })

    @staticmethod
    def format_journal(line):
        return "({0},'{1}','{2}',{3},{4},'{5}','{6}',{7},{8},{9},{10},{11},{12}),".format(
            line['move_id'],
            line['date'],
            line['date_maturity'],
            line['operating_unit_id'],
            line['account_id'],
            line['name'],
            line['name'],
            line['currency_id'],
            line['journal_id'],
            line['credit'],
            line['debit'],
            line['amount_currency'],
            line['company_id'])

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('calculate', 'confirm'))]

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('calculate', 'confirm', 'approve', 'reject'):
                raise ValidationError(_('[Warning] Draft record can be deleted.'))

            try:
                return super(TPMManagementModel, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))


class TPMManagementLineModel(models.Model):
    _name = 'tpm.calculation.line'
    _order = 'branch_id ASC'

    name = fields.Char(string="Name")
    income = fields.Float(string='Income Amount', compute='_compute_income_expense', digits=(14, 2))
    expense = fields.Float(string='Expense Amount', compute='_compute_income_expense', digits=(14, 2))
    branch_id = fields.Many2one('operating.unit', string='Branch', required=True)
    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)
    line_id = fields.Many2one("tpm.calculation", string='Line')
    pl_status = fields.Selection([('income', 'Income'), ('expense', 'Expense')], compute='_compute_income_expense',
                                 string='Income/Expense')
    branch_line_ids = fields.One2many('tpm.branch.calculation.line', 'branch_line_id')

    @api.multi
    @api.depends('branch_line_ids')
    def _compute_income_expense(self):
        for rec in self:
            income = sum([val.income for val in rec.branch_line_ids])
            expense = sum([val.expense for val in rec.branch_line_ids])
            balance = income - expense
            if balance > 0:
                rec.income = abs(balance)
                rec.expense = 0
                rec.pl_status = 'income'
            else:
                rec.income = 0
                rec.expense = abs(balance)
                rec.pl_status = 'expense'


class TPMBranchManagementLineModel(models.Model):
    _name = 'tpm.branch.calculation.line'
    _order = 'date ASC'

    income = fields.Float(string='Income Amount', digits=(14, 2))
    expense = fields.Float(string='Expense Amount', digits=(14, 2))
    balance = fields.Float(string='Balance', digits=(14, 2))
    branch_id = fields.Many2one('operating.unit', string='Branch', required=True)
    date = fields.Date(string='Date', required=True)
    income_rate = fields.Float(string='Income Rate (%)', required=True)
    expense_rate = fields.Float(string='Expense Rate (%)', required=True)
    branch_line_id = fields.Many2one('tpm.calculation.line')
    pl_status = fields.Selection([('income', 'Income'), ('expense', 'Expense')], string='Income/Expense')
