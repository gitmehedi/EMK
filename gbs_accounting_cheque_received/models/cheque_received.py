from odoo import models, fields, api
import datetime


class ChequeReceived(models.Model):
    _inherit = 'account.payment'
    _name = 'accounting.cheque.received'
    #_inherit = ['mail.thread', 'ir.needaction_mixin']
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
    payment_type = fields.Selection([('inbound', 'Inbound'), ('outbound', 'Outbound')], required=True, default = 'inbound')

    @api.multi
    def _get_name(self):
        for n in self:
            n.name = 'Customer Payments1'

    name = fields.Char(string='Name', compute='_get_name')
    partner_id = fields.Many2one('res.partner', string="Customer", required=True)
    bank_name = fields.Many2one('res.bank', string='Bank', required=True)
    branch_name = fields.Char(string='Branch Name', required=True, )
    date_on_cheque = fields.Date('Date On Cheque', required=True)
    cheque_amount = fields.Float(string='Amount', required=True, )
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    is_cheque_payment = fields.Boolean(string='Cheque Payment', default=True)
    company_id = fields.Many2one('res.company', string='Company', ondelete='cascade',
                                 default=lambda self: self.env.user.company_id, readonly='True')

    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)

    @api.multi
    def _get_payment_method(self):
        for pay in self:
            pay.payment_method_id = 2


    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', compute='_get_payment_method')
    currency_id = fields.Many2one('res.currency', string='Currency',)

    payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money')],
                                    string='Payment Type', required=True, default='inbound')

    @api.multi
    def _compute_journal(self):
        for jour in self:
            jour.journal_id = jour.env.user.company_id.bank_journal_ids.id

    journal_id = fields.Many2one('account.journal',compute='_compute_journal')

    # Update customer's Credit Limit. Basically plus cheque amount with Customer Credit Limit
    @api.multi
    def updateCustomersCreditLimit(self):
        for cust in self:
            res_partner_credit_limit = cust.env['res.partner.credit.limit'].search(
                [('partner_id', '=', cust.partner_id.id),
                 ('state', '=', 'approve')], order='assign_id DESC', limit=1)

            #Cheque Amount with Credit limit of customer; it should not exceed customer's original Credit Limit.
            if cust.sale_order_id.credit_sales_or_lc == 'credit_sales' \
                    and cust.sale_order_id.partner_id.id == cust.partner_id.id:

                update_cust_credits = res_partner_credit_limit.remaining_credit_limit + cust.cheque_amount

                if update_cust_credits > res_partner_credit_limit.value:
                    res_partner_credit_limit.write({'remaining_credit_limit': res_partner_credit_limit.value})
                else:
                    res_partner_credit_limit.write({'remaining_credit_limit': update_cust_credits})


    # Decrese Customers Receivable amount when cheque is honored
    #@todo below method has some bugs, fix it
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
            #cash_rcv._create_payment_entry(cash_rcv.cheque_amount)

            # acc_move_line_pool = cash_rcv.env['account.move.line']
            # account_move = cash_rcv.env['account.move']
            #
            # seq = cash_rcv.env['ir.sequence'].next_by_code('account.move') or '/'
            #
            # move_vals = {}
            # move_vals['date'] = cash_rcv.date_on_cheque
            # move_vals['company_id'] = cash_rcv.company_id.id
            # move_vals['journal_id'] = cash_rcv.company_id.bank_journal_ids.id
            # move_vals['partner_id'] = cash_rcv.partner_id.id
            # move_vals['ref'] = ''
            # move_vals['matched_percentage'] = 0
            # move_vals['state'] = 'posted'
            # move_vals['amount'] = cash_rcv.cheque_amount
            # move_vals['name'] = seq
            # move = account_move.create(move_vals)
            #
            # move_line_vals = {}
            # move_line_vals['partner_id'] = cash_rcv.partner_id.id
            # move_line_vals['name'] = "Customer Payment"
            # move_line_vals['debit'] = 0
            # move_line_vals['credit'] = move.amount
            # move_line_vals['move_id'] = move.id
            # move_line_vals['date_maturity'] = cash_rcv.date_on_cheque
            # move_line_vals['journal_id'] = move.journal_id.id
            # move_line_vals['state'] = 'posted'
            # move_line_vals['account_id'] = cash_rcv.company_id.bank_journal_ids.default_debit_account_id.id
            # res = acc_move_line_pool.create(move_line_vals)
            #
            # move_line_vals2 = {}
            # move_line_vals2['partner_id'] = cash_rcv.partner_id.id
            # move_line_vals2['name'] = cash_rcv.name
            # move_line_vals2['debit'] = move.amount
            # move_line_vals2['credit'] = 0
            # move_line_vals2['move_id'] = move.id
            # move_line_vals2['date_maturity'] = cash_rcv.date_on_cheque
            # move_line_vals2['journal_id'] = move.journal_id.id
            # move_line_vals2['account_id'] = cash_rcv.partner_id.property_account_receivable_id.id
            # move_line_vals2['state'] = 'posted'
            #
            # res2 = acc_move_line_pool.create(move_line_vals2)
            #
            # Update Customer's Credit Limit & Receilable Amount
            cash_rcv.updateCustomersCreditLimit()
            cash_rcv.updateCustomersReceivableAmount()

            cash_rcv.state = 'honoured'



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