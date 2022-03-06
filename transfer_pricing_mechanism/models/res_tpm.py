import time
from datetime import datetime, timedelta

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, Warning
from psycopg2 import IntegrityError


class ResTPM(models.Model):
    _name = 'res.tpm'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'TPM Management'
    _order = 'id desc'

    def _default_from_date(self):
        return self.env.user.company_id.batch_date

    name = fields.Char('Name', size=200, track_visibility='onchange', readonly=True)
    branch_id = fields.Many2one('operating.unit', string='Branch', readonly=True,
                                states={'draft': [('readonly', False)]}, required=True)
    date = fields.Date(string='From Date', default=_default_from_date, required=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    to_date = fields.Date(string='To Date', required=True, readonly=True,
                          states={'draft': [('readonly', False)]})
    total_income = fields.Float(string="Total Income", compute="_compute_income_expense", store=True)
    total_expense = fields.Float(string="Total Expense", compute="_compute_income_expense", store=True)
    balance = fields.Float(string="Difference", compute="_compute_income_expense", store=True)
    journal_id = fields.Many2one('account.move', string='Journal', readonly=True)
    line_ids = fields.One2many('res.tpm.branch', 'line_id', string='Lines', readonly=True)
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
        pass

        # for rec in self:
        #     rec.total_income = sum([val.income for val in rec.line_ids])
        #     rec.total_expense = sum([val.expense for val in rec.line_ids])
        #     rec.balance = abs(rec.total_income - rec.total_expense)

    @api.one
    def act_draft(self):
        if self.state == 'calculate':
            self.write({
                'state': 'draft',
            })

    def get_tpm_rate(self, rate_type='local'):
        tpm_config = self.env['res.tpm.config.settings'].search([])
        if not tpm_config:
            raise Warning(_("Please configure proper settings for TPM"))
        days = tpm_config.days_in_fy

        if rate_type == 'local':
            query = """SELECT RTP.BRANCH_ID,
                        RTPL.ACCOUNT_ID,
                        RTPL.CURRENCY_ID,
                        RTPL.INCOME_RATE,
                        RTPL.EXPENSE_RATE
                    FROM RES_TPM_PRODUCT RTP
                    LEFT JOIN RES_TPM_PRODUCT_LINE RTPL ON (RTPL.LINE_ID = RTP.ID);"""
        else:
            query = """SELECT RTP.BRANCH_ID,
                            RTPL.ACCOUNT_ID,
                            RTPL.CURRENCY_ID,
                            RTPL.INCOME_RATE,
                            RTPL.EXPENSE_RATE
                        FROM RES_TPM_PRODUCT RTP
                        LEFT JOIN RES_TPM_PRODUCT_FC_LINE RTPL ON (RTPL.LINE_ID = RTP.ID);"""

        self.env.cr.execute(query)

        record = {}
        for rec in self.env.cr.fetchall():
            income_rate = ((rec[3] / 100) / days)
            expense_rate = ((rec[4] / 100) / days)
            rate = "{0}{1}{2}".format(rec[0], rec[1], rec[2])
            record[rate] = {
                'income_rate': rec[3],
                'income_rate_ratio': expense_rate,
                'expense_rate': rec[4],
                'expense_rate_ratio': expense_rate,
            }

        return record

    @api.multi
    def calculate_tpm(self):
        if self.state == 'draft':
            self.line_ids.unlink()

            local_rate = self.get_tpm_rate()
            foreign_rate = self.get_tpm_rate('others')

            branch = self.env['operating.unit'].sudo().search([('active', '=', True),
                                                               ('pending', '=', False)])
            branch_lines = {}
            for val in branch:
                branch_lines[val.id] = {}

            cur_date = fields.Date.today()
            fy = self.env['date.range'].search([('date_end', '>=', cur_date), ('date_start', '<=', cur_date),
                                                ('type_id.fiscal_year', '=', True), ('active', '=', True)])
            if not fy:
                raise Warning(_("Financial is not available. Please create current financial year."))
            stat_time = time.time()
            fy_start_date = fy.date_start
            d1 = datetime.strptime(self.date, "%Y-%m-%d")
            d2 = datetime.strptime(self.to_date, "%Y-%m-%d")
            no_of_days = (d2 - d1).days + 1
            for day in range(0, no_of_days):
                start_date = datetime.strftime(d1 + timedelta(days=day), '%Y-%m-%d')
                end_date = datetime.strftime(d1 + timedelta(days=day), '%Y-%m-%d')
                tpm_date = start_date

                query = """SELECT aa.id AS branch,
                                   COALESCE(init.account,inc_exp.account),
	                               COALESCE(init.currency,inc_exp.currency),
                                   COALESCE(inc_exp.credit, 0) AS credit,
                                   COALESCE(inc_exp.debit, 0) AS debit,
                                   (COALESCE(inc_exp.credit, 0) - COALESCE(inc_exp.debit, 0) + COALESCE(init.balance, 0)) AS balance,
                                   COALESCE(init.balance, 0) AS init_bal
                            FROM operating_unit aa
                            LEFT JOIN (SELECT aml.operating_unit_id AS branch,
                                               aml.account_id AS account,
                                               aml.currency_id AS currency,
                                              COALESCE((SUM(aml.credit) - SUM(aml.debit)), 0) AS balance
                                        FROM account_move_line aml
                                        LEFT JOIN account_move am
                                           ON (am.id = aml.move_id)
                                        WHERE aml.account_id IN (SELECT id FROM account_account WHERE code ~ '[1234].*' AND level_id=6)
                                              AND am.is_cbs=TRUE
                                              AND (aml.date >= '%s'
                                              AND aml.date < '%s') 
                                        GROUP  BY aml.operating_unit_id,
                                                  aml.account_id,
                                                  aml.currency_id) init ON (init.branch = aa.id)
                            LEFT JOIN (SELECT aml.operating_unit_id AS branch,
                                              aml.account_id AS account,
                                              aml.currency_id AS currency,
                                              COALESCE(SUM(aml.debit), 0) AS debit,
                                              COALESCE(SUM(aml.credit), 0) AS credit
                                        FROM account_move_line aml
                                        LEFT JOIN account_move am
                                           ON (am.id = aml.move_id)
                                        WHERE account_id in (SELECT id FROM account_account WHERE code ~ '[1234].*' AND level_id=6)
                                             AND am.is_cbs=TRUE
                                              AND (aml.date >= '%s'
                                              AND aml.date <= '%s')
                                        GROUP  BY aml.operating_unit_id,
                                                  aml.account_id,
                                                  aml.currency_id) inc_exp ON (inc_exp.branch = aa.id)
                            WHERE aa.active=True 
                                  AND aa.pending=False
                            ORDER BY aa.id ASC""" % (
                    fy_start_date, end_date, start_date, end_date)

                self.env.cr.execute(query)
                for bal in self.env.cr.fetchall():
                    branch_id = bal[0]
                    if tpm_date not in branch_lines[branch_id]:
                        branch_lines[branch_id][tpm_date] = []

                    check_rate = "{0}{1}{2}".format(bal[0], bal[1], bal[2])
                    if check_rate not in local_rate:
                        continue
                    else:
                        income = local_rate[check_rate]['income_rate']
                        income_ratio = local_rate[check_rate]['income_rate_ratio']
                        expense = local_rate[check_rate]['expense_rate']
                        expense_ratio = local_rate[check_rate]['expense_rate_ratio']

                    if bal[5] > 0:
                        debit_amount = round(abs(bal[5] * income_ratio), 2)
                        credit_amount = 0.0
                    else:
                        debit_amount = 0.0
                        credit_amount = round(abs(bal[5]) * expense_ratio, 2)

                    line = {
                        'account_id': bal[1],
                        'income': credit_amount,
                        'expense': debit_amount,
                        'balance': bal[5],
                        'pl_status': 'expense' if bal[5] > 0 else 'income',
                        'date': start_date,
                        'income_rate': income,
                        'expense_rate': expense
                    }
                    branch_lines[branch_id][tpm_date].append(line)

            rate_entry = ''
            count = 0
            cr_dt = fields.Datetime.now()
            for key, value in branch_lines.items():
                line = self.line_ids.create({
                    'name': self.id,
                    'branch_id': key,
                    'from_date': self.date,
                    'to_date': self.to_date,
                    'line_id': self.id,
                })
                for val, val_key in value.items():
                    date_entry = line.line_ids.create({
                        'date': val,
                        'line_id': line.id,
                    })
                    for rate in val_key:
                        count = count + 1
                        if count % 1000 == 0:
                            print
                            "-----------{0}--------".format(count / 1000)
                        # date_entry.line_ids.create({
                        #     'account_id': rate['account_id'],
                        #     'income': rate['income'],
                        #     'expense': rate['expense'],
                        #     'balance': rate['balance'],
                        #     'date': rate['date'],
                        #     'income_rate': rate['income_rate'],
                        #     'expense_rate': rate['expense_rate'],
                        #     'line_id': date_entry.id
                        # })
                        user_id = self.env.user.id
                        rate_entry += "({0},{1},{2},{3},'{4}',{5},{6},{7},{8},{9},'{10}','{11}'),".format(
                            rate['account_id'],
                            rate['income'],
                            rate['expense'],
                            rate['balance'],
                            rate['date'],
                            rate['income_rate'],
                            rate['expense_rate'],
                            date_entry.id,
                            user_id, user_id,
                            cr_dt, cr_dt)

            if not rate_entry:
                raise ValidationError(_("Proper information/Debit should not be empty."))
            query = """INSERT INTO res_tpm_branch_daily_product 
                                                (account_id,income,expense,balance,date,income_rate,expense_rate,line_id,create_uid,write_uid,create_date,write_date)  
                                                VALUES %s""" % rate_entry[:-1]
            self.env.cr.execute(query)
            print
            "------------------------{0}".format(time.time() - stat_time)
            # self.write({'state': 'calculate'})

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
            date = self.env.user.company_id.batch_date
            journal_entry = ""
            tpm_config = self.env['account.app.config'].search([('config_type', '=', 'tpm')])
            if not tpm_config:
                raise Warning(_("Please configure proper settings for TPM"))
            company = self.env.user.company_id
            journal = tpm_config.journal_id.id
            current_currency = company.currency_id.id
            income_account = tpm_config.tpm_income_account_id.id
            income_seq = tpm_config.tpm_income_seq_id.id
            expense_account = tpm_config.tpm_expense_account_id.id
            expense_seq = tpm_config.tpm_expense_seq_id.id
            move = self.env['account.move'].create({
                'ref': 'TPM in [{0}] with ref {1}'.format(self.date, self.name),
                'date': date,
                'journal_id': journal,
                'operating_unit_id': self.branch_id.id,
                'is_cr': True,
            })
            for rec in self.line_ids:
                branch = rec.sudo().branch_id
                if rec.income == 0 and rec.expense == 0:
                    continue

                if rec.income > 0:
                    credit_account_id = income_account
                    credit_seq_id = income_seq
                    debit_account_id = expense_account
                    debit_seq_id = expense_seq
                    income_cr_cr = rec.income
                    income_cr_dr = 0
                    income_dr_cr = 0
                    income_dr_dr = rec.income
                    credit_branch_id = branch.id
                    debit_branch_id = self.branch_id.id
                    credit_nar = "%s of %s" % ('Income', branch.display_name.replace("'", ""))
                    debit_nar = "%s of %s" % ('Income', branch.display_name.replace("'", ""))
                else:
                    credit_account_id = income_account
                    credit_seq_id = income_seq
                    debit_account_id = expense_account
                    debit_seq_id = expense_seq
                    income_cr_cr = rec.expense
                    income_cr_dr = 0
                    income_dr_cr = 0
                    income_dr_dr = rec.expense
                    credit_branch_id = self.branch_id.id
                    debit_branch_id = branch.id
                    credit_nar = "%s of %s" % ('Expense', branch.display_name.replace("'", ""))
                    debit_nar = "%s of %s" % ('Expense', branch.display_name.replace("'", ""))

                credit = {
                    'name': credit_nar,
                    'date': date,
                    'date_maturity': date,
                    'account_id': credit_account_id,
                    'sub_operating_unit_id': credit_seq_id,
                    'credit': income_cr_cr,
                    'debit': income_cr_dr,
                    'journal_id': journal,
                    'operating_unit_id': credit_branch_id,
                    'currency_id': current_currency,
                    'amount_currency': 0.0,
                    'move_id': move.id,
                    'company_id': company.id,
                    'is_bgl': 'not_check',
                }
                debit = {
                    'name': debit_nar,
                    'date': date,
                    'date_maturity': date,
                    'account_id': debit_account_id,
                    'sub_operating_unit_id': debit_seq_id,
                    'credit': income_dr_cr,
                    'debit': income_dr_dr,
                    'journal_id': journal,
                    'operating_unit_id': debit_branch_id,
                    'currency_id': current_currency,
                    'amount_currency': 0.0,
                    'move_id': move.id,
                    'company_id': company.id,
                    'is_bgl': 'not_check',
                }
                journal_entry += self.format_journal(credit)
                journal_entry += self.format_journal(debit)

            if not journal_entry:
                raise ValidationError(_("Credit/Debit should not be empty."))

            query = """INSERT INTO account_move_line 
                                    (move_id, date,date_maturity, operating_unit_id, account_id, name,ref, currency_id, journal_id,
                                    credit,debit,amount_currency,company_id,is_bgl,sub_operating_unit_id)  
                                    VALUES %s""" % journal_entry[:-1]
            self.env.cr.execute(query)

            if move.state == 'draft':
                move.write({'maker_id': self.maker_id.id,
                            'approver_id': self.env.user.id})
                move.post()

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
        return "({0},'{1}','{2}',{3},{4},'{5}','{6}',{7},{8},{9},{10},{11},{12},'{13}',{14}),".format(
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
            line['company_id'],
            line['is_bgl'],
            line['sub_operating_unit_id'],
        )

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('calculate', 'confirm'))]

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('calculate', 'confirm', 'approve', 'reject'):
                raise ValidationError(_('[Warning] Draft record can be deleted.'))

            try:
                return super(ResTPM, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))


class ResTPMBranch(models.Model):
    _name = 'res.tpm.branch'
    _order = 'branch_id ASC'

    name = fields.Char(string="Name")
    income = fields.Float(string='Income Amount', compute='_compute_income_expense', digits=(14, 2))
    expense = fields.Float(string='Expense Amount', compute='_compute_income_expense', digits=(14, 2))
    branch_id = fields.Many2one('operating.unit', string='Branch', required=True)
    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)
    line_id = fields.Many2one("res.tpm", string='Line', ondelete='cascade')
    pl_status = fields.Selection([('income', 'Income'), ('expense', 'Expense')], compute='_compute_income_expense',
                                 string='Income/Expense')
    line_ids = fields.One2many('res.tpm.branch.daily', 'line_id')

    @api.multi
    @api.depends('line_ids')
    def _compute_income_expense(self):
        for rec in self:
            income = sum([val.income for val in rec.line_ids])
            expense = sum([val.expense for val in rec.line_ids])
            balance = income - expense
            if balance > 0:
                rec.income = abs(balance)
                rec.expense = 0
                rec.pl_status = 'income'
            else:
                rec.income = 0
                rec.expense = abs(balance)
                rec.pl_status = 'expense'


class ResTPMBranchDaily(models.Model):
    _name = 'res.tpm.branch.daily'
    _order = 'date ASC'

    income = fields.Float(string='Income Amount', compute='_compute_income_expense', digits=(14, 2))
    expense = fields.Float(string='Expense Amount', compute='_compute_income_expense', digits=(14, 2))
    balance = fields.Float(string='Balance', digits=(14, 2))
    date = fields.Date(string='Date', required=True)
    pl_status = fields.Selection([('income', 'Income'), ('expense', 'Expense')], string='Income/Expense')
    line_id = fields.Many2one('res.tpm.branch', ondelete='cascade')
    line_ids = fields.One2many('res.tpm.branch.daily.product', 'line_id')

    @api.multi
    @api.depends('line_ids')
    def _compute_income_expense(self):
        for rec in self:
            income = sum([val.income for val in rec.line_ids])
            expense = sum([val.expense for val in rec.line_ids])
            balance = income - expense
            if balance > 0:
                rec.income = abs(balance)
                rec.expense = 0
                rec.pl_status = 'income'
            else:
                rec.income = 0
                rec.expense = abs(balance)
                rec.pl_status = 'expense'


class ResTPMBranchDailyProduct(models.Model):
    _name = 'res.tpm.branch.daily.product'
    _order = 'date ASC'

    account_id = fields.Many2one('account.account', string='Account', track_visibility='onchange')
    income = fields.Float(string='Income Amount', digits=(14, 2), track_visibility='onchange')
    expense = fields.Float(string='Expense Amount', digits=(14, 2), track_visibility='onchange')
    balance = fields.Float(string='Balance', digits=(14, 2), track_visibility='onchange')
    date = fields.Date(string='Date', required=True, track_visibility='onchange')
    income_rate = fields.Float(string='Income Rate (%)', required=True, track_visibility='onchange')
    expense_rate = fields.Float(string='Expense Rate (%)', required=True, track_visibility='onchange')
    line_id = fields.Many2one('res.tpm.branch.daily', ondelete='cascade')
    pl_status = fields.Selection([('income', 'Income'), ('expense', 'Expense')], string='Income/Expense')
