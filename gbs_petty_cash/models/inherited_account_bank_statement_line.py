from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime


class InheritedBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    name = fields.Char(string='Label', size=40, required=True)

    @api.constrains('date')
    def _check_date(self):
        if self.date:
            date_object = datetime.strptime(self.date, '%Y-%m-%d').date()
            if date_object > date.today():
                raise ValidationError(_("You cannot input future transaction!"))

    @api.depends('type_of_operation', 'is_petty_cash_journal')
    @api.constrains('amount')
    def _check_amount_val(self):
        if self.is_petty_cash_journal and self.amount == 0:
            raise ValidationError('Transaction amount can not be 0')
        if self.is_petty_cash_journal and self.type_of_operation == 'cash_in' and self.amount < 0:
            raise ValidationError('Cash In amount can not be negative')
        elif self.is_petty_cash_journal and self.type_of_operation == 'cash_out' and self.amount > 0:
            raise ValidationError('Cash Out amount can not be positive')

    @api.depends('statement_id')
    def _check_journal(self):
        for rec in self:
            if rec.statement_id:
                if rec.statement_id.is_petty_cash_journal:
                    rec.is_petty_cash_journal = True
                else:
                    rec.is_petty_cash_journal = False

    is_petty_cash_journal = fields.Boolean(compute="_check_journal")
    is_reconciled = fields.Boolean(tracking=True)

    @api.depends('statement_id')
    def statement_type_compute(self):
        for rec in self:
            if rec.statement_id:
                rec.type_of_operation = rec.statement_id.type_of_operation

    type_of_operation = fields.Char(compute='statement_type_compute')
