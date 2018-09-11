from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import datetime


class ChequeReceived(models.Model):
    _name = 'accounting.cheque.received'
    _inherit = ['mail.thread']
    _order = 'id DESC'
    _description = "Cheque Info"


    state = fields.Selection([
        ('draft', 'Cheque Entry'),
        ('received', 'Confirm'),
        ('deposited', 'Deposit to Bank'),
        ('honoured', 'Honoured'),
        ('dishonoured', 'Dishonoured'),
        ('returned', 'Returned to Customer'),
    ], readonly=True, track_visibility='onchange', copy=False, default='draft')

    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor')], default='customer')
    payment_type = fields.Selection([('inbound', 'Inbound'), ('outbound', 'Outbound')], required=True,
                                    default='inbound')

    @api.multi
    def _get_name(self):
        for n in self:
            n.name = 'Customer Payments'


    name = fields.Char(string='Name', compute='_get_name')
    partner_id = fields.Many2one('res.partner', domain=[('parent_id', '=', False),('active', '=', True), ('customer', '=', True)], string="Customer", required=True, states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})
    bank_name = fields.Many2one('res.bank', string='Bank', required=True,states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})
    branch_name = fields.Char(string='Branch Name', required=True, states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})
    date_on_cheque = fields.Date('Date On Cheque', required=True, states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})
    cheque_amount = fields.Float(string='Amount', required=True, states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})
    is_cheque_payment = fields.Boolean(string='Cheque Payment', default=True)
    company_id = fields.Many2one('res.company', string='Company', ondelete='cascade',
                                 default=lambda self: self.env.user.company_id, readonly='True', states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})

    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False, states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})

    #@todo : Update this field
    is_this_payment_checked = fields.Boolean(string='is_this_payment_checked', default=False)
    cheque_no = fields.Char(string='Cheque No',states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})

    @api.multi
    def _get_payment_method(self):
        for pay in self:
            pay_method_pool = pay.env['account.payment.method'].search([('payment_type', '=', 'inbound')], limit=1)
            pay.payment_method_id = pay_method_pool.id


    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type',
                                   )
    currency_id = fields.Many2one('res.currency', string='Currency', states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})

    payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money')],
                                string='Payment Type', required=True, default='inbound')

    @api.onchange('partner_id')
    def _on_change_partner_id(self):
        for pay in self:
            pay_method_pool = pay.env['account.payment.method'].search([('payment_type', '=', 'inbound')], limit=1)
            pay.payment_method_id = pay_method_pool.id


    journal_id = fields.Many2one('account.journal', string='Payment Journal',
                                 states={'returned': [('readonly', True)], 'dishonoured': [('readonly', True)],
                                         'honoured': [('readonly', True)], 'received': [('readonly', True)],
                                         'deposited': [('readonly', True)]},domain=[('type', '=', 'bank')])

    @api.constrains('currency_id')
    def _check_currency_with_companys_currency(self):
        if self.journal_id and self.currency_id:
            if self.currency_id != self.journal_id.company_id.currency_id:
                raise ValidationError('Payment Journal Currency and Cheque Received Currency must be same')


    @api.constrains('cheque_amount')
    def _check_negative_amount_value(self):
        if self.cheque_amount < 0:
            raise ValidationError('The payment amount must be strictly positive.')

        if self.cheque_amount == 0:
            raise ValidationError('The payment amount must be greater than zero')


    # Update customer's Credit Limit. Basically plus cheque amount with Customer Credit Limit
    @api.multi
    def updateCustomersCreditLimit(self):
        for cust in self:
            res_partner_credit_limit = cust.env['res.partner.credit.limit'].search(
                [('partner_id', '=', cust.partner_id.id),
                 ('state', '=', 'approve')], order='id DESC', limit=1)

            # Cheque Amount with Credit limit of customer; it should not exceed customer's original Credit Limit.
            if cust.sale_order_id.credit_sales_or_lc == 'credit_sales' \
                    and cust.sale_order_id.partner_id.id == cust.partner_id.id:

                update_cust_credits = res_partner_credit_limit.remaining_credit_limit + cust.cheque_amount

                if update_cust_credits > res_partner_credit_limit.value:
                    res_partner_credit_limit.write({'remaining_credit_limit': res_partner_credit_limit.value})
                else:
                    res_partner_credit_limit.write({'remaining_credit_limit': update_cust_credits})


    @api.multi
    def action_honoured(self):
        for cash in self:
            cash.action_journal_entry_bank()
            #cash.updateCustomersCreditLimit()

            cash.state = 'honoured'


    @api.multi
    def action_journal_entry_bank(self):

        for cr in self:
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = cr.date_on_cheque

            move_dict = {
                'journal_id': cr.journal_id.id,
                'date': date,
            }

            debit_account_id = cr.partner_id.property_account_receivable_id
            credit_account_id = cr.journal_id.default_credit_account_id

            if debit_account_id:

                amount_currency = 0
                debit_amount = cr.cheque_amount > 0.0 and cr.cheque_amount or 0.0
                credit_amount = cr.cheque_amount < 0.0 and -cr.cheque_amount or 0.0
                currency_id = cr.journal_id.currency_id.id


                if cr.journal_id.currency_id:
                    if cr.journal_id.currency_id != cr.company_id.currency_id:
                        amount_currency = cr.cheque_amount
                        amount = amount_currency / cr.journal_id.currency_id.rate
                        debit_amount = amount > 0.0 and amount or 0.0
                        credit_amount = amount < 0.0 and -amount or 0.0


                debit_line = (0, 0, {
                    'name': debit_account_id.name,
                    'partner_id': cr.partner_id.id,
                    'account_id': debit_account_id.id,
                    'journal_id': cr.journal_id.id,
                    'currency_id': currency_id,
                    'amount_currency': amount_currency,
                    'date': date,
                    'debit': debit_amount,
                    'credit': credit_amount,
                    'cheque_received_id':cr.id, # update only to debit leg
                })

                line_ids.append(debit_line)
                debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

            if credit_account_id:

                amount_currency = 0
                debit_amount = cr.cheque_amount < 0.0 and -cr.cheque_amount or 0.0
                credit_amount = cr.cheque_amount > 0.0 and cr.cheque_amount or 0.0
                currency_id = cr.journal_id.currency_id.id

                if cr.journal_id.currency_id:
                    if cr.journal_id.currency_id != cr.company_id.currency_id:
                        amount_currency = cr.cheque_amount
                        amount = amount_currency / cr.journal_id.currency_id.rate
                        debit_amount = amount < 0.0 and -amount or 0.0
                        credit_amount = amount > 0.0 and amount or 0.0

                credit_line = (0, 0, {
                    'name': credit_account_id.name,
                    'partner_id': cr.partner_id.id,
                    'account_id': credit_account_id.id,
                    'journal_id': cr.journal_id.id,
                    'currency_id': currency_id,
                    'amount_currency': -amount_currency, # amount_currency is negative when it is in credit
                    'date': date,
                    'debit': debit_amount,
                    'credit': credit_amount,
                })
                line_ids.append(credit_line)
                credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

        move_dict['line_ids'] = line_ids
        move = self.env['account.move'].create(move_dict)
        move.post()


    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('accounting.cheque.received') or '/'
        vals['name'] = seq
        return super(ChequeReceived, self).create(vals)


    @api.multi
    def action_received(self):
        for cr in self:
            cr.state = 'received'


    @api.multi
    def action_deposited(self):
        for cr in self:
            cr.state = 'deposited'


    @api.multi
    def action_dishonoured(self):
        for cr in self:
            cr.state = 'dishonoured'


    @api.multi
    def action_returned_to_customer(self):
        for cr in self:
            cr.state = 'returned'
