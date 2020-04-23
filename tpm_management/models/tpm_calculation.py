from odoo import api, fields, models, _, SUPERUSER_ID
from psycopg2 import IntegrityError
from odoo.exceptions import ValidationError


class TPMManagementModel(models.Model):
    _name = 'tpm.calculation'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'TPM Management'
    _order = 'id desc'

    name = fields.Char('Name', size=200, track_visibility='onchange', readonly=True)
    branch_id = fields.Many2one('operating.unit', string='Branch', readonly=True,
                                states={'draft': [('readonly', False)]}, required=True)
    date = fields.Date(string='Date', default=fields.Date.today, readonly=True, required=True)
    total_profit = fields.Float(string="Total Profit", compute="_compute_profit_loss")
    total_loss = fields.Float(string="Total Loss", compute="_compute_profit_loss")
    balance = fields.Float(string="Difference", compute="_compute_profit_loss")
    journal_id = fields.Many2one('account.move', string='Journal Entry', readonly=True)
    line_ids = fields.One2many('tpm.calculation.line', 'line_id', string='Lines', readonly=True)
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'),
                              ('calculate', 'Calculate'),
                              ('confirm', 'Confirmed'),
                              ('approve', 'Approved'),
                              ('reject', 'Rejected')],
                             default='draft', string='Status', track_visibility='onchange')

    # @api.constrains("date")
    # def check_date(self):
    #     if self.date:
    #         obj = self.search([('date', '=', self.date)])
    #         if len(obj) > 0:
    #             raise ValidationError(_("Same date TPM is not possible."))

    @api.multi
    @api.depends('line_ids')
    def _compute_profit_loss(self):
        for rec in self:
            rec.total_profit = sum([val.profit for val in rec.line_ids])
            rec.total_loss = sum([val.loss for val in rec.line_ids])
            rec.balance = abs(rec.total_profit - rec.total_loss)

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
            general_account = company.tpm_general_account_id.id
            income_rate = company.income_rate / 100
            expense_rate = company.expense_rate / 100
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
                if bal[3] > 0:
                    debit_amount = 0.0
                    credit_amount = round(bal[3] * income_rate, 2)
                else:
                    debit_amount = round(abs(bal[3] * expense_rate), 2)
                    credit_amount = 0.0

                self.line_ids.create({
                    'name': self.id,
                    'profit': credit_amount,
                    'loss': debit_amount,
                    'pl_status': 'profit' if bal[3] > 0 else 'loss',
                    'branch_id': branch_id,
                    'date': fields.Datetime.now(),
                    'line_id': self.id,
                })

                self.state = 'calculate'

    @api.multi
    def act_confirm(self):
        if self.state == 'calculate':
            name = self.env['ir.sequence'].next_by_code('tpm.calculation') or ''
            self.write({
                'name': name,
                'state': 'confirm',
                'maker_id': self.env.user.id,
            })

    @api.one
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
                credit = {
                    'name': name,
                    'date': date,
                    'date_maturity': date,
                    'account_id': income_account if rec.profit > 0 else general_account,
                    'debit': rec.profit,
                    'credit': rec.loss,
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
                    'account_id': general_account if rec.profit > 0 else expense_account,
                    'credit': rec.profit,
                    'debit': rec.loss,
                    'journal_id': journal,
                    'operating_unit_id': rec.branch_id.id,
                    'currency_id': current_currency,
                    'amount_currency': 0.0,
                    'move_id': move.id,
                    'company_id': company.id,
                }
                journal_entry += self.format_journal(credit)
                journal_entry += self.format_journal(debit)

            query = """INSERT INTO account_move_line 
                                    (move_id, date,date_maturity, operating_unit_id, account_id, name,ref, currency_id, journal_id,
                                    credit,debit,amount_currency,company_id)  
                                    VALUES %s""" % journal_entry[:-1]
            self.env.cr.execute(query)

            if move.state == 'draft':
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
    _order = 'id desc'

    name = fields.Char(string="Name")
    profit = fields.Float(string='Profit Amount', digits=(14, 2))
    loss = fields.Float(string='Loss Amount', digits=(14, 2))
    branch_id = fields.Many2one('operating.unit', string='Branch', required=True)
    date = fields.Date(string='Date', default=fields.Date.today, required=True)
    line_id = fields.Many2one("tpm.calculation", string='Line')
    pl_status = fields.Selection([('profit', 'Profit'), ('loss', 'Loss')], string='Profit/Loss')
