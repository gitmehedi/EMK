from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import datetime


class ChequeReceived(models.Model):
    _inherit = 'account.payment'
    _name = 'accounting.cheque.received'
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'name'

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
    partner_id = fields.Many2one('res.partner', domain=[('active', '=', True), ('customer', '=', True)], string="Customer", required=True, states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})
    bank_name = fields.Many2one('res.bank', string='Bank', required=True,states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})
    branch_name = fields.Char(string='Branch Name', required=True, states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})
    date_on_cheque = fields.Date('Date On Cheque', required=True, states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})
    cheque_amount = fields.Float(string='Amount', required=True, states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})
    is_cheque_payment = fields.Boolean(string='Cheque Payment', default=True)
    company_id = fields.Many2one('res.company', string='Company', ondelete='cascade',
                                 default=lambda self: self.env.user.company_id, readonly='True', states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})

    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False, states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})


    # @api.multi
    # def action_payslip_done(self):
    #
    #     for slip in self:
    #         line_ids = []
    #         debit_sum = 0.0
    #         credit_sum = 0.0
    #         date = slip.date or slip.date_to
    #
    #         name = "Test Rabbi"
    #         move_dict = {
    #             'narration': name,
    #             #'ref': slip.number,
    #             'journal_id': slip.journal_id.id,
    #             'date': date,
    #         }
    #         for line in slip.details_by_salary_rule_category:
    #             amount = slip.cheque_amount
    #
    #             debit_account_id = line.salary_rule_id.account_debit.id
    #             credit_account_id = line.salary_rule_id.account_credit.id
    #
    #             if debit_account_id:
    #                 debit_line = (0, 0, {
    #                     'name': line.name,
    #                     'partner_id': line._get_partner_id(credit_account=False),
    #                     'account_id': debit_account_id,
    #                     'journal_id': slip.journal_id.id,
    #                     'date': date,
    #                     'debit': amount > 0.0 and amount or 0.0,
    #                     'credit': amount < 0.0 and -amount or 0.0,
    #                     'analytic_account_id': line.salary_rule_id.analytic_account_id.id,
    #                     'tax_line_id': line.salary_rule_id.account_tax_id.id,
    #                 })
    #                 line_ids.append(debit_line)
    #                 debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
    #
    #             if credit_account_id:
    #                 credit_line = (0, 0, {
    #                     'name': line.name,
    #                     'partner_id': line._get_partner_id(credit_account=True),
    #                     'account_id': credit_account_id,
    #                     'journal_id': slip.journal_id.id,
    #                     'date': date,
    #                     'debit': amount < 0.0 and -amount or 0.0,
    #                     'credit': amount > 0.0 and amount or 0.0,
    #                     'analytic_account_id': line.salary_rule_id.analytic_account_id.id,
    #                     'tax_line_id': line.salary_rule_id.account_tax_id.id,
    #                 })
    #                 line_ids.append(credit_line)
    #                 credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
    #
    #         if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
    #             acc_id = slip.journal_id.default_credit_account_id.id
    #             if not acc_id:
    #                 raise UserError(_('The Expense Journal "%s" has not properly configured the Credit Account!') % (
    #                 slip.journal_id.name))
    #             adjust_credit = (0, 0, {
    #                 'name': _('Adjustment Entry'),
    #                 'partner_id': False,
    #                 'account_id': acc_id,
    #                 'journal_id': slip.journal_id.id,
    #                 'date': date,
    #                 'debit': 0.0,
    #                 'credit': debit_sum - credit_sum,
    #             })
    #             line_ids.append(adjust_credit)
    #
    #         elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
    #             acc_id = slip.journal_id.default_debit_account_id.id
    #             if not acc_id:
    #                 raise UserError(_('The Expense Journal "%s" has not properly configured the Debit Account!') % (
    #                 slip.journal_id.name))
    #             adjust_debit = (0, 0, {
    #                 'name': _('Adjustment Entry'),
    #                 'partner_id': False,
    #                 'account_id': acc_id,
    #                 'journal_id': slip.journal_id.id,
    #                 'date': date,
    #                 'debit': credit_sum - debit_sum,
    #                 'credit': 0.0,
    #             })
    #             line_ids.append(adjust_debit)
    #         move_dict['line_ids'] = line_ids
    #         move = self.env['account.move'].create(move_dict)
    #         slip.write({'move_id': move.id, 'date': date})
    #         move.post()
    #     return super(HrPayslip, self).action_payslip_done()
    #
    #

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


    @api.multi
    def _compute_journal(self):
        for jour in self:
            jour.journal_id = jour.env.user.company_id.bank_journal_ids.id


    journal_id = fields.Many2one('account.journal', compute='_compute_journal')


    @api.constrains('cheque_amount')
    def _check_negative_amount_value(self):
        if self.cheque_amount < 0:
            raise ValidationError('The payment amount must be strictly positive.')


    # Update customer's Credit Limit. Basically plus cheque amount with Customer Credit Limit
    @api.multi
    def updateCustomersCreditLimit(self):
        for cust in self:
            res_partner_credit_limit = cust.env['res.partner.credit.limit'].search(
                [('partner_id', '=', cust.partner_id.id),
                 ('state', '=', 'approve')], order='assign_id DESC', limit=1)

            # Cheque Amount with Credit limit of customer; it should not exceed customer's original Credit Limit.
            if cust.sale_order_id.credit_sales_or_lc == 'credit_sales' \
                    and cust.sale_order_id.partner_id.id == cust.partner_id.id:

                update_cust_credits = res_partner_credit_limit.remaining_credit_limit + cust.cheque_amount

                if update_cust_credits > res_partner_credit_limit.value:
                    res_partner_credit_limit.write({'remaining_credit_limit': res_partner_credit_limit.value})
                else:
                    res_partner_credit_limit.write({'remaining_credit_limit': update_cust_credits})


    # Decrese Customers Receivable amount when cheque is honored
    # @todo below method has some bugs, fix it
    @api.multi
    def updateCustomersReceivableAmount(self):
        for cust in self:
            res_partner_pool = cust.env['res.partner'].search([('id', '=', cust.partner_id.id)])

            if cust.sale_order_id.credit_sales_or_lc == 'credit_sales':
                # Customer's Receivable amount is actually minus value
                update_cust_receivable_amount = res_partner_pool.credit + cust.cheque_amount
                res_partner_pool.property_account_payable_id.write({'credit': update_cust_receivable_amount})


    @api.multi
    def action_honoured(self):
        for cash_rcv in self:
            # cash_rcv.cheque_amount = 0 # Test val
            cash_rcv._create_payment_entry(cash_rcv.cheque_amount)

            # Update Customer's Credit Limit & Receilable Amount
            cash_rcv.updateCustomersCreditLimit()
            cash_rcv.updateCustomersReceivableAmount()

            cash_rcv.state = 'honoured'



    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('accounting.cheque.received') or '/'
        vals['name'] = seq
        vals['amount'] = 12
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
