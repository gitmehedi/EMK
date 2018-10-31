from odoo import api, fields, models

import time, datetime


class PaymentEntryReconciled(models.TransientModel):
    _name = 'payment.entry.reconciled'
    _description = 'Payment Entry Reconciled'
    _rec_name = 'name'

    name = fields.Char(string='name', default='Payment Entry Reconciled')
    date = fields.Date(string='Date', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)])
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], default='draft')

    """ Relational Fields"""
    line_ids = fields.One2many('payment.entry.reconciled.line', 'parent_id', string="Unreconciled Lines",
                               ondelete='cascade')

    """ Methods go below """


    def action_clear_accounts(self):
        for rec in self:
            for line in rec.line_ids:
                if line.clear_acc_receivable is True:
                    rec.clear_receivable_accounts(line.amount, line.company_id, line.partner_id)

                    # Update flag for Customer Payment Entry
                    if line.cheque_received_id:
                        line.cheque_received_id.write({'is_entry_receivable_cleared': True})

                    if line.payment_id:
                        line.payment_id.write({'is_entry_receivable_cleared_payments': True})


    def clear_receivable_accounts(self, amt, company_id, partner_id):
        for rec in self:

            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = rec.date

            move_dict = {
                'journal_id': company_id.journal_id.id,
                'date': date,
            }

            amount = amt

            debit_account_id = company_id.account_receive_clearing_acc
            credit_account_id = partner_id.property_account_receivable_id

            if debit_account_id:
                debit_line = (0, 0, {
                    'name': debit_account_id.name,
                    'partner_id': partner_id.id,
                    'account_id': debit_account_id.id,
                    'journal_id': company_id.journal_id.id,
                    'date': date,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                })

                line_ids.append(debit_line)
                debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

            if credit_account_id:
                credit_line = (0, 0, {
                    'name': credit_account_id.name,
                    'partner_id': partner_id.id,
                    'account_id': credit_account_id.id,
                    'journal_id': company_id.journal_id.id,
                    'date': date,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                })

                line_ids.append(credit_line)
                credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

            # # Update flag for Customer Payment Entry
            # for line in rec.line_ids:
            #     if line.cheque_received_id:
            #         line.cheque_received_id.write({'is_entry_receivable_cleared': True})
            #
            #     if line.payment_id:
            #         line.payment_id.write({'is_entry_receivable_cleared_payments': True})

        move_dict['line_ids'] = line_ids
        move = self.env['account.move'].create(move_dict)
        move.post()

    def action_search(self):

        for pay_en in self:
            pay_en.line_ids.unlink()

            if not pay_en.partner_id.id:
                payment_pool = pay_en.env['account.payment'].search(
                    [('is_entry_receivable_cleared_payments', '=', False), ('payment_date', '<=', pay_en.date),
                     ('state', '=', 'posted')])

                cheque_rcv_pool = pay_en.env['accounting.cheque.received'].search(
                    [('is_entry_receivable_cleared', '=', False), ('date_on_cheque', '<=', pay_en.date),
                     ('state', '=', 'honoured')])

            elif pay_en.partner_id:
                payment_pool = pay_en.env['account.payment'].search(
                    [('is_entry_receivable_cleared_payments', '=', False), ('payment_date', '<=', pay_en.date),
                     ('partner_id', '=', pay_en.partner_id.id),
                     ('state', '=', 'posted')])

                cheque_rcv_pool = pay_en.env['accounting.cheque.received'].search(
                    [('is_entry_receivable_cleared', '=', False), ('date_on_cheque', '<=', pay_en.date),
                     ('partner_id', '=', pay_en.partner_id.id),
                     ('state', '=', 'honoured')])

            vals = []

            for payments in payment_pool:
                vals.append((0, 0, {'amount': payments.amount,
                                    # 'journal_id': payments.journal_id,
                                    'currency_id': payments.currency_id.id,
                                    'partner_id': payments.partner_id.id,
                                    'company_id': payments.company_id.id,
                                    'payment_id': payments.id,
                                    }))



            for cheq in cheque_rcv_pool:
                vals.append((0, 0, {'amount': cheq.cheque_amount,
                                    # 'journal_id': cheq.journal_id,
                                    'currency_id': cheq.currency_id.id,
                                    'partner_id': cheq.partner_id.id,
                                    'company_id': cheq.company_id.id,
                                    'cheque_received_id': cheq.id,
                                    }))

            # show the updated list
            pay_en.line_ids = vals



class PaymentEntryReconciledLine(models.TransientModel):
    _name = 'payment.entry.reconciled.line'

    amount = fields.Float(string='Amount', readonly=True)
    clear_acc_receivable = fields.Boolean(string='r')
    # journal_id = fields.Many2one('account.journal', string='Payment Journal', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)], readonly=True)
    company_id = fields.Many2one('res.company', string='Company')
    cheque_received_id = fields.Many2one('accounting.cheque.received', string='Cheque Received ID')
    payment_id = fields.Many2one('account.payment', string='Customer Payment ID')

    """ Relational Fields"""
    parent_id = fields.Many2one('payment.entry.reconciled', ondelete='cascade')

