from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class InheritAccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def action_journal_entry_cash_treatment(self):

        for cr in self:
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = cr.payment_date

            move_dict = {
                'journal_id': cr.journal_id.id,
                'date': date,
            }

            amount = cr.amount

            suspense_ac_cash = cr.env['conf.credit.acc'].search([]) # Expect only one entry

            if len(suspense_ac_cash) == 0:
                raise ValidationError('Suspense Account is not set')

            debit_account_id = cr.partner_id.property_account_receivable_id
            credit_account_id = suspense_ac_cash.cash_suspense_account

            if debit_account_id:
                debit_line = (0, 0, {
                    'name': cr.sale_order_id.name,
                    'partner_id': cr.partner_id.id,
                    'account_id': debit_account_id.id,
                    'journal_id': cr.journal_id.id,
                    'date': date,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                })

                line_ids.append(debit_line)
                debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

            if credit_account_id:
                credit_line = (0, 0, {
                    'name': cr.sale_order_id.name,
                    'partner_id': cr.partner_id.id,
                    'account_id': credit_account_id.id,
                    'journal_id': cr.journal_id.id,
                    'date': date,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                })
                line_ids.append(credit_line)
                credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

        move_dict['line_ids'] = line_ids
        move = self.env['account.move'].create(move_dict)
        move.post()




    @api.multi
    def post(self):
        res = super(InheritAccountPayment, self).post()

        if self.sale_order_id.type_id.sale_order_type == 'cash':
            self.action_journal_entry_cash_treatment()

        return res
