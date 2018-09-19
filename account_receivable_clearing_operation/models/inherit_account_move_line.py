from odoo import api, fields, models, _


class InheritAccountMoveLine(models.Model):
    _inherit = 'account.move.line'



    def action_reconcile_journal_entry(self):
        for mv_line in self:
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = mv_line.date

            move_dict = {
                'journal_id': mv_line.company_id.journal_id.id,
                'date': date,
            }

            amount = mv_line.credit # only credit entry

            debit_account_id =  mv_line.company_id.account_receive_clearing_acc
            credit_account_id = mv_line.partner_id.property_account_receivable_id

            if debit_account_id:
                debit_line = (0, 0, {
                    'name': debit_account_id.name,
                    'partner_id': mv_line.partner_id.id,
                    'account_id': debit_account_id.id,
                    'journal_id': mv_line.company_id.journal_id.id,
                    'date': date,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                })

                line_ids.append(debit_line)
                debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

            if credit_account_id:
                credit_line = (0, 0, {
                    'name': credit_account_id.name,
                    'partner_id': mv_line.partner_id.id,
                    'account_id': credit_account_id.id,
                    'journal_id': mv_line.company_id.journal_id.id,
                    'date': date,
                    'debit':  amount < 0.0 and -amount or 0.0,
                    'credit':  amount > 0.0 and amount or 0.0,
                })

                line_ids.append(credit_line)
                credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']


        move_dict['line_ids'] = line_ids
        move = self.env['account.move'].create(move_dict)
        move.post()

        #@todo Update the reconcile flag TRUE after Journal Entry is successful
        self.write({'reconciled': True})







