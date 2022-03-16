import itertools
import time

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, Warning
from psycopg2 import IntegrityError


class ResTPMProduct(models.Model):
    _name = 'res.tpm.product'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'TPM Products'
    _order = 'branch_id asc'

    def _default_from_date(self):
        return self.env.user.company_id.batch_date

    name = fields.Char('Name', size=200, track_visibility='onchange', readonly=True,
                       states={'draft': [('readonly', False)]})
    date = fields.Date(string='Date', default=_default_from_date, required=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    branch_id = fields.Many2one('operating.unit', string='Branch', readonly=True,
                                states={'draft': [('readonly', False)]})
    line_ids = fields.One2many('res.tpm.product.line', 'line_id', string='Lines', readonly=True)
    line_fc_ids = fields.One2many('res.tpm.product.fc.line', 'line_id', string='Lines', readonly=True)
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('approve', 'Approved'),
                              ('reject', 'Rejected')],
                             default='draft', string='Status', track_visibility='onchange')

    # @api.constrains("date", "to_date")
    # def check_date(self):
    #     # date = self._default_from_date()
    #     # if date != self.date:
    #     #     raise ValidationError(_("From Date value in not appropriate."))
    #     if self.date > self.to_date:
    #         raise ValidationError(_("From Date should not be greater than To Date."))

    # @api.multi
    # @api.depends('line_ids')
    # def _compute_income_expense(self):
    #     for rec in self:
    #         rec.total_income = sum([val.income for val in rec.line_ids])
    #         rec.total_expense = sum([val.expense for val in rec.line_ids])
    #         rec.balance = abs(rec.total_income - rec.total_expense)

    @api.one
    def act_draft(self):
        if self.state == 'calculate':
            self.write({
                'state': 'draft',
            })

    @api.multi
    def act_config_product(self):
        if self.state == 'draft':
            # self.line_ids.unlink()

            accounts = self.env['account.account'].search([('state', '=', 'approve'), ('pending', '=', False),
                                                           ('active', '=', True), ('level_id.name', '=', 'Layer 5')])
            branch = self.env['operating.unit'].search([('state', '=', 'approve'),
                                                        ('pending', '=', False),
                                                        ('active', '=', True)])

            product_all = list(itertools.product(branch.ids, accounts.ids))
            product_exists = [(val.branch_id, val.account_id) for val in self.line_ids]

            tpm_config = self.env['res.tpm.config.settings'].search([], order='id desc', limit=1)
            if not tpm_config:
                raise Warning(_("Please configure proper settings for TPM"))
            income_rate = tpm_config.income_rate
            expense_rate = tpm_config.expense_rate

            start_time = time.time()

            line = []
            entry = ''
            for rec in product_all:
                date = fields.Date.today()
                datetime = fields.Datetime.now()
                user_id = self.env.user.id
                entry += "({0},{1},{2},{3},'{4}',{5},{6},'{7}','{8}',),".format(rec[1], income_rate,
                                                                                expense_rate, date, self.id, user_id,
                                                                                user_id, datetime, datetime)

            if not entry:
                raise ValidationError(_("Proper information/Debit should not be empty."))

            query = """INSERT INTO res_tpm_product_line 
                                    (account_id,income_rate,expense_rate,date,line_id,create_uid,write_uid,create_date,write_date)  
                                    VALUES %s""" % entry[:-1]
            self.env.cr.execute(query)
            # print("--- %s seconds ---" % (time.time() - start_time))
            # self.write({'line_ids': line})
            print("--- %s seconds ---" % (time.time() - start_time))
            # return
            # excl_br = tpm_config.excl_br_ids.ids
            # branch = self.env['operating.unit'].sudo().search(
            #     [('active', '=', True), ('pending', '=', False), ('id', 'not in', excl_br)])
            # branch_lines = {}
            # for val in branch:
            #     branch_lines[val.id] = []

            # cur_date = fields.Date.today()
            # fy = self.env['date.range'].search([('date_end', '>=', cur_date), ('date_start', '<=', cur_date),
            #                                     ('type_id.fiscal_year', '=', True), ('active', '=', True)])
            # if not fy:
            #     raise Warning(_("Financial is not available. Please create current financial year."))
            #
            # fy_start_date = fy.date_start
            # d1 = datetime.strptime(self.date, "%Y-%m-%d")
            # d2 = datetime.strptime(self.to_date, "%Y-%m-%d")
            # no_of_days = (d2 - d1).days + 1
            # for day in range(0, no_of_days):
            #     start_date = d1 + timedelta(days=day)
            #     end_date = d1 + timedelta(days=day)
            #
            #     query = """SELECT aa.id,
            #                        COALESCE(trial.credit, 0) AS credit,
            #                        COALESCE(trial.debit, 0) AS debit,
            #                        (COALESCE(trial.credit, 0) - COALESCE(trial.debit, 0) + COALESCE(init.balance, 0)) AS balance,
            #                        COALESCE(init.balance, 0) AS init_bal
            #                 FROM operating_unit aa
            #                 LEFT JOIN (SELECT aml.operating_unit_id AS id,
            #                                   COALESCE(SUM(aml.debit), 0) AS debit,
            #                                   COALESCE(SUM(aml.credit), 0) AS credit
            #                             FROM account_move_line aml
            #                             LEFT JOIN account_move am
            #                                ON (am.id = aml.move_id)
            #                             WHERE aml.account_id=%s
            #                                   AND am.is_cbs=TRUE
            #                                   AND (aml.date >= '%s'
            #                                   AND aml.date <= '%s')
            #                             GROUP  BY aml.operating_unit_id) trial ON (trial.id = aa.id)
            #                 LEFT JOIN (SELECT aml.operating_unit_id AS id,
            #                                   COALESCE((SUM(aml.credit) - SUM(aml.debit)), 0) AS balance
            #                             FROM account_move_line aml
            #                             LEFT JOIN account_move am
            #                                ON (am.id = aml.move_id)
            #                             WHERE aml.account_id=%s
            #                                   AND am.is_cbs=TRUE
            #                                   AND (aml.date >= '%s'
            #                                   AND aml.date < '%s')
            #                             GROUP  BY aml.operating_unit_id) init ON (init.id = aa.id)
            #                 WHERE aa.active=True
            #                       AND aa.pending=False
            #                 ORDER BY aa.id ASC""" % (
            #         general_account, start_date, end_date, general_account, fy_start_date, end_date)
            #
            #     self.env.cr.execute(query)
            #     for bal in self.env.cr.fetchall():
            #         branch_id = bal[0]
            #         if branch_id in excl_br:
            #             continue
            #
            #         if bal[3] > 0:
            #             debit_amount = round(abs(bal[3] * expense_rate), 2)
            #             credit_amount = 0.0
            #         else:
            #             debit_amount = 0.0
            #             credit_amount = round(abs(bal[3]) * income_rate, 2)
            #
            #         line = {
            #             'income': credit_amount,
            #             'expense': debit_amount,
            #             'balance': bal[3],
            #             'pl_status': 'expense' if bal[3] > 0 else 'income',
            #             'branch_id': branch_id,
            #             'date': start_date,
            #             'income_rate': tpm_config.income_rate,
            #             'expense_rate': tpm_config.expense_rate,
            #             'branch_line_id': 0,
            #         }
            #         branch_lines[bal[0]].append(line)
            #
            # for key, value in branch_lines.items():
            #     line = self.line_ids.create({
            #         'name': self.id,
            #         'branch_id': key,
            #         'from_date': self.date,
            #         'to_date': self.to_date,
            #         'line_id': self.id,
            #     })
            #     for val in value:
            #         val['branch_line_id'] = line.id
            #         line.branch_line_ids.create(val)
            #
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
                return super(ResTPMProduct, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))

    @staticmethod
    def format_journal(line):
        return "({0},{1},{2},'{3}',{4},{5}),".format(
            line['line_id'],
            line['branch_id'],
            line['account_id'],
            line['date'],
            line['income_rate'],
            line['expense_rate'],
        )


class ResTPMProductLine(models.Model):
    _name = 'res.tpm.product.line'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'account_id ASC'

    account_id = fields.Many2one('account.account', string='Chart of Account', required=True,
                                 track_visibility='onchange')
    income_rate = fields.Float(string='Income Rate', digits=(14, 2), track_visibility='onchange')
    expense_rate = fields.Float(string='Expense Rate', digits=(14, 2), track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string='Currency', track_visibility='onchange')
    date = fields.Date(string='Date', required=True, track_visibility='onchange')
    line_id = fields.Many2one("res.tpm.product", string='Line', track_visibility='onchange')


class ResTPMProductFCLine(models.Model):
    _name = 'res.tpm.product.fc.line'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'account_id ASC'

    account_id = fields.Many2one('account.account', string='Chart of Account', required=True,
                                 track_visibility='onchange')
    income_rate = fields.Float(string='Income Rate', digits=(14, 2), track_visibility='onchange')
    expense_rate = fields.Float(string='Expense Rate', digits=(14, 2), track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string='Currency', track_visibility='onchange')
    date = fields.Date(string='Date', required=True, track_visibility='onchange')
    line_id = fields.Many2one("res.tpm.product", string='Line', track_visibility='onchange')
