from datetime import datetime, timedelta

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, Warning
from psycopg2 import IntegrityError


class ResTPM(models.Model):
    _name = 'res.tpm'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Transfer Pricing Mechanism'
    _order = 'id desc'

    def _default_from_date(self):
        return self.env.user.company_id.batch_date

    name = fields.Char('Name', size=200, track_visibility='onchange', readonly=True)
    branch_id = fields.Many2one('operating.unit', string='Branch', readonly=True, required=True,
                                states={'draft': [('readonly', False)]})
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

    def get_tpm_rate(self):
        tpm_config = self.env['res.tpm.config.settings'].search([], order='id desc', limit=1)
        if not tpm_config:
            raise Warning(_("Please configure proper settings for TPM"))
        days = tpm_config.days_in_fy

        query = """SELECT RATE.BRANCH_ID,
                        RATE.ACCOUNT_ID,
                        RATE.CURRENCY_ID,
                        RATE.INCOME_RATE,
                        RATE.EXPENSE_RATE
                    FROM
                        (SELECT RTP.BRANCH_ID,
                                RTPL.ACCOUNT_ID,
                                RTPL.CURRENCY_ID,
                                RTPL.INCOME_RATE,
                                RTPL.EXPENSE_RATE
                            FROM RES_TPM_PRODUCT RTP
                            LEFT JOIN RES_TPM_PRODUCT_LINE RTPL ON (RTPL.LINE_ID = RTP.ID)
                            UNION ALL SELECT RTP.BRANCH_ID,
                                RTPL.ACCOUNT_ID,
                                RTPL.CURRENCY_ID,
                                RTPL.INCOME_RATE,
                                RTPL.EXPENSE_RATE
                            FROM RES_TPM_PRODUCT RTP
                            LEFT JOIN RES_TPM_PRODUCT_FC_LINE RTPL ON (RTPL.LINE_ID = RTP.ID)) AS RATE
                    ORDER BY ACCOUNT_ID ASC"""

        self.env.cr.execute(query)

        record = {}
        for rec in self.env.cr.fetchall():
            rate = "{0}{1}{2}".format(rec[0], rec[1], rec[2])
            record[rate] = {
                'income_rate': rec[3],
                'income_rate_ratio': ((rec[3] / 100) / days),
                'expense_rate': rec[4],
                'expense_rate_ratio': ((rec[4] / 100) / days),
            }

        return record

    @api.multi
    def calculate_tpm(self):
        if self.state == 'draft':
            self.line_ids.unlink()

            local_rate = self.get_tpm_rate()

            branch_all = self.env['operating.unit'].sudo().search([('active', '=', True), ('pending', '=', False)])
            setting = self.env['res.tpm.config.settings'].search([], order='id desc', limit=1)
            if not setting:
                raise ValidationError(_("Please configure settings data"))

            branch = branch_all - setting.excl_br_ids
            branch_lines = {}
            for val in branch:
                branch_lines[val.id] = {}

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
                start_date = datetime.strftime(d1 + timedelta(days=day), '%Y-%m-%d')
                end_date = datetime.strftime(d1 + timedelta(days=day), '%Y-%m-%d')
                tpm_date = start_date

                query = """SELECT TPM.BRANCH,
                                TPM.ACCOUNT,
                                TPM.CURRENCY,
                                AA.CODE,
                                COALESCE(SUM(TPM.BALANCE),0) AS BALANCE,
                                COALESCE(SUM(TPM.DEBIT),0) AS DEBIT,
                                COALESCE(SUM(TPM.CREDIT),0) AS CREDIT
                            FROM
                                (SELECT AML.OPERATING_UNIT_ID AS BRANCH,
                                        AML.ACCOUNT_ID AS ACCOUNT,
                                        AML.CURRENCY_ID AS CURRENCY,
                                        COALESCE((SUM(AML.CREDIT) - SUM(AML.DEBIT)), 0) AS BALANCE,
                                        0 AS DEBIT,
                                        0 AS CREDIT
                                    FROM ACCOUNT_MOVE_LINE AML
                                    LEFT JOIN ACCOUNT_MOVE AM ON (AM.ID = AML.MOVE_ID)
                                    WHERE AML.ACCOUNT_ID IN
                                            (SELECT ID FROM ACCOUNT_ACCOUNT WHERE CODE ~ '^[1234]' AND LEVEL_ID = 6)
                                        AND AM.IS_CBS = TRUE
                                        AND (AML.DATE >= '%s' AND AML.DATE < '%s') 
                                    GROUP  BY AML.OPERATING_UNIT_ID,
                                            AML.ACCOUNT_ID,
                                            AML.CURRENCY_ID,
                                            AML.DEBIT,
                                            AML.CREDIT
                                 UNION ALL 
                                 SELECT AML.OPERATING_UNIT_ID AS BRANCH,
                                        AML.ACCOUNT_ID AS ACCOUNT,
                                        AML.CURRENCY_ID AS CURRENCY,
                                        0 AS BALANCE,
                                        COALESCE(SUM(AML.DEBIT),0) AS DEBIT,
                                        COALESCE(SUM(AML.CREDIT),0) AS CREDIT
                                    FROM ACCOUNT_MOVE_LINE AML
                                    LEFT JOIN ACCOUNT_MOVE AM ON (AM.ID = AML.MOVE_ID)
                                    WHERE ACCOUNT_ID in
                                            (SELECT ID FROM ACCOUNT_ACCOUNT WHERE CODE ~ '^[1234]' AND LEVEL_ID = 6)
                                        AND AM.IS_CBS = TRUE
                                        AND (AML.DATE >= '%s' AND AML.DATE <= '%s') 
                                    GROUP  BY AML.OPERATING_UNIT_ID,
                                            AML.ACCOUNT_ID,
                                            AML.CURRENCY_ID ) AS TPM
                            LEFT JOIN ACCOUNT_ACCOUNT AA ON (AA.ID = TPM.ACCOUNT)
                            WHERE TPM.BRANCH NOT IN %s
                            GROUP BY TPM.BRANCH,
                                TPM.ACCOUNT,
                                TPM.CURRENCY,
                                AA.CODE
                            ORDER BY TPM.BRANCH DESC""" % (
                    fy_start_date, end_date, start_date, end_date, tuple(setting.excl_br_ids.ids))

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

                    if int(bal[3][0]) in [1, 3]:
                        income_acc = 'income'
                    else:
                        income_acc = 'expense'

                    balance = bal[6] - bal[5] + bal[4]

                    if income_acc == 'income':
                        debit_amount = round(abs(balance * income_ratio), 2)
                        credit_amount = 0.0
                    else:
                        debit_amount = 0.0
                        credit_amount = round(abs(balance) * expense_ratio, 2)

                    line = {
                        'account_id': bal[1],
                        'income': credit_amount,
                        'expense': debit_amount,
                        'balance': balance,
                        'pl_status': income_acc,
                        'date': start_date,
                        'income_rate': income,
                        'expense_rate': expense,
                        'currency': bal[2],
                    }
                    branch_lines[branch_id][tpm_date].append(line)

            local_rate, foreign_rate = '', ''
            cr_dt = fields.Datetime.now()
            user_id = self.env.user.id

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
                    income, expense, balance = 0, 0, 0
                    for rate in val_key:
                        if rate['pl_status'] == 'income':
                            income += (rate['income'] - rate['expense'])
                        if rate['pl_status'] == 'expense':
                            expense += (rate['income'] - rate['expense'])

                        if rate['currency'] == 56:
                            local_rate += "({0},{1},{2},{3},'{4}',{5},{6},'{7}',{8},{9},{10},{11},'{12}','{13}'),".format(
                                rate['account_id'],
                                rate['income'],
                                rate['expense'],
                                rate['balance'],
                                rate['date'],
                                rate['income_rate'],
                                rate['expense_rate'],
                                rate['pl_status'],
                                rate['currency'],
                                date_entry.id,
                                user_id, user_id,
                                cr_dt, cr_dt)
                        else:
                            foreign_rate += "({0},{1},{2},{3},'{4}',{5},{6},'{7}',{8},{9},{10},{11},'{12}','{13}'),".format(
                                rate['account_id'],
                                rate['income'],
                                rate['expense'],
                                rate['balance'],
                                rate['date'],
                                rate['income_rate'],
                                rate['expense_rate'],
                                rate['pl_status'],
                                rate['currency'],
                                date_entry.id,
                                user_id, user_id,
                                cr_dt, cr_dt)

                    balance = abs(income) - abs(expense)
                    pl_status = 'income' if balance > 0 else 'expense'
                    date_entry.write({'income': abs(income),
                                      'expense': abs(expense),
                                      'balance': abs(balance),
                                      'pl_status': pl_status})

            if local_rate:
                local_query = """INSERT INTO res_tpm_branch_daily_product_local
                                 (account_id,income,expense,balance,date,income_rate,expense_rate,pl_status,currency_id,line_id,create_uid,write_uid,create_date,write_date)  
                                 VALUES %s""" % local_rate[:-1]
                self.env.cr.execute(local_query)
            if foreign_rate:
                foreign_query = """INSERT INTO res_tpm_branch_daily_product_foreign
                                   (account_id,income,expense,balance,date,income_rate,expense_rate,pl_status,currency_id,line_id,create_uid,write_uid,create_date,write_date)  
                                   VALUES %s""" % foreign_rate[:-1]
                self.env.cr.execute(foreign_query)

            self.write({'state': 'calculate'})

    @api.multi
    def act_confirm(self):
        if self.state == 'calculate':
            name = self.env['ir.sequence'].next_by_code('res.tpm') or ''
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
            tpm_config = self.env['res.tpm.config.settings'].search([], order='id desc', limit=1)
            if not tpm_config:
                raise Warning(_("Please configure proper settings for TPM"))

            company = self.env.user.company_id
            journal = tpm_config.journal_id.id
            current_currency = company.currency_id.id
            general_account = tpm_config.tpm_general_account_id.id
            general_seq = tpm_config.tpm_general_seq_id.id
            income_account = tpm_config.tpm_income_account_id.id
            income_seq = tpm_config.tpm_income_seq_id.id
            expense_account = tpm_config.tpm_expense_account_id.id
            expense_seq = tpm_config.tpm_expense_seq_id.id
            move = self.env['account.move'].create({
                'ref': 'TPM in [{0}] with ref {1}'.format(self.date, self.name),
                'date': date,
                'journal_id': journal,
                'is_cr': True
            })

            for rec in self.line_ids:
                branch = rec.sudo().branch_id
                if rec.income == 0 and rec.expense == 0:
                    continue

                income, expense = {}, {}
                if rec.income > 0:
                    inc_br_nar = "FTP Income Jan, 2022, Treasury Dept"
                    inc_tr_nar = "FTP Expense Jan, 2022, Corporate Head Office"

                    income['inc_br_cr'] = {
                        'name': inc_br_nar,
                        'date': date,
                        'date_maturity': date,
                        'account_id': income_account,
                        'sub_operating_unit_id': income_seq,
                        'credit': rec.income,
                        'debit': 0.0,
                        'amount_currency': 0.0,
                        'journal_id': journal,
                        'operating_unit_id': branch.id,
                        'currency_id': current_currency,
                        'move_id': move.id,
                        'company_id': company.id,
                        'is_bgl': 'not_check',
                    }
                    income['inc_br_dr'] = {
                        'name': inc_br_nar,
                        'date': date,
                        'date_maturity': date,
                        'account_id': general_account,
                        'sub_operating_unit_id': general_seq,
                        'credit': 0.0,
                        'amount_currency': 0.0,
                        'debit': rec.income,
                        'journal_id': journal,
                        'operating_unit_id': branch.id,
                        'currency_id': current_currency,
                        'move_id': move.id,
                        'company_id': company.id,
                        'is_bgl': 'not_check',
                    }
                    income['inc_tr_cr'] = {
                        'name': inc_tr_nar,
                        'date': date,
                        'date_maturity': date,
                        'account_id': expense_account,
                        'sub_operating_unit_id': expense_seq,
                        'credit': 0.0,
                        'debit': rec.income,
                        'amount_currency': 0.0,
                        'journal_id': journal,
                        'operating_unit_id': self.branch_id.id,
                        'currency_id': current_currency,
                        'move_id': move.id,
                        'company_id': company.id,
                        'is_bgl': 'not_check',
                    }
                    income['inc_tr_dr'] = {
                        'name': inc_tr_nar,
                        'date': date,
                        'date_maturity': date,
                        'account_id': general_account,
                        'sub_operating_unit_id': general_seq,
                        'credit': rec.income,
                        'debit': 0.0,
                        'amount_currency': 0.0,
                        'journal_id': journal,
                        'operating_unit_id': self.branch_id.id,
                        'currency_id': current_currency,
                        'move_id': move.id,
                        'company_id': company.id,
                        'is_bgl': 'not_check',
                    }
                    journal_entry += self.format_journal(income['inc_br_cr'])
                    journal_entry += self.format_journal(income['inc_br_dr'])
                    journal_entry += self.format_journal(income['inc_tr_cr'])
                    journal_entry += self.format_journal(income['inc_tr_dr'])
                else:
                    exp_br_nar = "FTP Expense Jan, 2022, Treasury Dept"
                    exp_tr_nar = "FTP Income Jan, 2022, Principal Branch"

                    expense['exp_br_dr'] = {
                        'name': exp_br_nar,
                        'date': date,
                        'date_maturity': date,
                        'account_id': expense_account,
                        'sub_operating_unit_id': expense_seq,
                        'credit': 0.0,
                        'debit': rec.expense,
                        'amount_currency': 0.0,
                        'journal_id': journal,
                        'operating_unit_id': branch.id,
                        'currency_id': current_currency,
                        'move_id': move.id,
                        'company_id': company.id,
                        'is_bgl': 'not_check',
                    }
                    expense['exp_br_cr'] = {
                        'name': exp_br_nar,
                        'date': date,
                        'date_maturity': date,
                        'account_id': general_account,
                        'sub_operating_unit_id': general_seq,
                        'credit': rec.expense,
                        'debit': 0.0,
                        'amount_currency': 0.0,
                        'journal_id': journal,
                        'operating_unit_id': branch.id,
                        'currency_id': current_currency,
                        'move_id': move.id,
                        'company_id': company.id,
                        'is_bgl': 'not_check',
                    }
                    expense['exp_tr_cr'] = {
                        'name': exp_tr_nar,
                        'date': date,
                        'date_maturity': date,
                        'account_id': income_account,
                        'sub_operating_unit_id': income_seq,
                        'credit': rec.expense,
                        'debit': 0.0,
                        'amount_currency': 0.0,
                        'journal_id': journal,
                        'operating_unit_id': self.branch_id.id,
                        'currency_id': current_currency,
                        'move_id': move.id,
                        'company_id': company.id,
                        'is_bgl': 'not_check',
                    }
                    expense['exp_tr_dr'] = {
                        'name': exp_tr_nar,
                        'date': date,
                        'date_maturity': date,
                        'account_id': general_account,
                        'sub_operating_unit_id': general_seq,
                        'credit': 0.0,
                        'debit': rec.expense,
                        'amount_currency': 0.0,
                        'journal_id': journal,
                        'operating_unit_id': branch.id,
                        'currency_id': current_currency,
                        'move_id': move.id,
                        'company_id': company.id,
                        'is_bgl': 'not_check',
                    }
                    journal_entry += self.format_journal(expense['exp_br_dr'])
                    journal_entry += self.format_journal(expense['exp_br_cr'])
                    journal_entry += self.format_journal(expense['exp_tr_cr'])
                    journal_entry += self.format_journal(expense['exp_tr_dr'])

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
        return [('state', 'in', ('draft', 'calculate', 'confirm'))]

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

    income = fields.Float(string='Income Amount', digits=(14, 2))
    expense = fields.Float(string='Expense Amount', digits=(14, 2))
    balance = fields.Float(string='Balance', digits=(14, 2))
    date = fields.Date(string='Date', required=True)
    pl_status = fields.Selection([('income', 'Income'), ('expense', 'Expense')], string='Income/Expense')
    line_id = fields.Many2one('res.tpm.branch', ondelete='cascade')
    line_local_ids = fields.One2many('res.tpm.branch.daily.product.local', 'line_id')
    line_foreign_ids = fields.One2many('res.tpm.branch.daily.product.foreign', 'line_id')


class ResTPMBranchDailyProductLocal(models.Model):
    _name = 'res.tpm.branch.daily.product.local'
    _order = 'date ASC'

    account_id = fields.Many2one('account.account', string='Account', track_visibility='onchange')
    income = fields.Float(string='Income Amount', digits=(14, 2), track_visibility='onchange')
    expense = fields.Float(string='Expense Amount', digits=(14, 2), track_visibility='onchange')
    balance = fields.Float(string='Balance', digits=(14, 2), track_visibility='onchange')
    date = fields.Date(string='Date', required=True, track_visibility='onchange')
    income_rate = fields.Float(string='Income Rate (%)', required=True, track_visibility='onchange')
    expense_rate = fields.Float(string='Expense Rate (%)', required=True, track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string='Currency', track_visibility='onchange')
    line_id = fields.Many2one('res.tpm.branch.daily', ondelete='cascade')
    pl_status = fields.Selection([('income', 'Income'), ('expense', 'Expense')], string='Income/Expense')


class ResTPMBranchDailyProductForeign(models.Model):
    _name = 'res.tpm.branch.daily.product.foreign'
    _order = 'date ASC'

    account_id = fields.Many2one('account.account', string='Account', track_visibility='onchange')
    income = fields.Float(string='Income Amount', digits=(14, 2), track_visibility='onchange')
    expense = fields.Float(string='Expense Amount', digits=(14, 2), track_visibility='onchange')
    balance = fields.Float(string='Balance', digits=(14, 2), track_visibility='onchange')
    date = fields.Date(string='Date', required=True, track_visibility='onchange')
    income_rate = fields.Float(string='Income Rate (%)', required=True, track_visibility='onchange')
    expense_rate = fields.Float(string='Expense Rate (%)', required=True, track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string='Currency', track_visibility='onchange')
    line_id = fields.Many2one('res.tpm.branch.daily', ondelete='cascade')
    pl_status = fields.Selection([('income', 'Income'), ('expense', 'Expense')], string='Income/Expense')
