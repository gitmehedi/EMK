from odoo import models, fields, api
import datetime


class ChequeReceived(models.Model):
    _name = 'accounting.cheque.received'
    _rec_name = 'name'

    state = fields.Selection([
        ('draft', 'Cheque Entry'),
        ('received', 'Confirm'),
        ('deposited', 'Deposit to Bank'),
        ('honoured', 'Honoured'),
        ('dishonoured', 'Dishonoured'),
        ('returned', 'Returned to Customer'),
    ], readonly=True, track_visibility='onchange', copy=False, default='draft')

    name = fields.Char(string='Name', readonly=True)
    partner_id = fields.Many2one('res.partner', string="Customer", required=True)
    bank_name = fields.Many2one('res.bank', string='Bank', required=True)
    branch_name = fields.Char(string='Branch Name', required=True, )
    date_on_cheque = fields.Date('Date On Cheque', required=True)
    cheque_amount = fields.Float(string='Amount', required=True, )
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', )
    is_cheque_payment = fields.Boolean(string='Cheque Payment', default=True)
    mr_sl_no = fields.Char(string='SL No.', )

    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('gbs_accounting_cheque_received'))

    """ Money receipt Q-Web report printing with unique serial no. """

    @api.multi
    def action_honoured(self):
        for cash_rcv in self:
            acc_move_line_pool = cash_rcv.env['account.move.line']
            account_move = cash_rcv.env['account.move']

            move_vals = {}
            move_vals['date'] = cash_rcv.date_on_cheque
            move_vals['company_id'] = cash_rcv.company_id.id
            move_vals['journal_id'] = cash_rcv.company_id.bank_journal_ids.id
            move_vals['partner_id'] = cash_rcv.partner_id.id
            move_vals['state'] = 'posted'
            move_vals['amount'] = cash_rcv.cheque_amount
            move = account_move.create(move_vals)

            move_line_vals = {}
            move_line_vals['partner_id'] = cash_rcv.partner_id.id
            move_line_vals['debit'] = cash_rcv.cheque_amount
            move_line_vals['credit'] = cash_rcv.cheque_amount
            move_line_vals['move_id'] = move.id
            move_line_vals['date_maturity'] = cash_rcv.date_on_cheque
            move_line_vals['currency_id'] = 3

            if move_line_vals['credit']:
                move_line_vals['account_id'] = cash_rcv.company_id.bank_journal_ids.default_debit_account_id.id
                move_line_vals['credit'] = cash_rcv.cheque_amount
                move_line_vals['credit_cash_basis'] = cash_rcv.cheque_amount
                move_line_vals['dedit_cash_basis'] = 0
                move_line_vals['balance_cash_basis'] = -cash_rcv.cheque_amount
                move_line_vals['debit'] = 0
                move_line_vals['name'] = "rabbi Customer Payment"
                move_line_vals['balance'] = -cash_rcv.cheque_amount
                move_line_vals['amount_currency'] = -cash_rcv.cheque_amount

                res = acc_move_line_pool.create(move_line_vals)

            if move_line_vals['debit']:
                move_line_vals['account_id'] = cash_rcv.partner_id.property_account_receivable_id.id
                move_line_vals['debit'] = cash_rcv.cheque_amount
                move_line_vals['credit'] = 0
                move_line_vals['credit_cash_basis'] = 0
                move_line_vals['dedit_cash_basis'] = cash_rcv.cheque_amount
                move_line_vals['balance_cash_basis'] = cash_rcv.cheque_amount
                move_line_vals['name'] = "rabbi CUST.IN/2018/0014"
                move_line_vals['balance'] = cash_rcv.cheque_amount
                move_line_vals['amount_currency'] = 0

                res2 = acc_move_line_pool.create(move_line_vals)


            cash_rcv.state = 'honoured'



    @api.model
    def create(self, vals):
        # acc_conf_setting_pool = self.env['account.config.settings'].search([], order='id desc', limit=1)
        seq = self.env['ir.sequence'].next_by_code('accounting.cheque.received') or '/'
        vals['name'] = seq
        return super(ChequeReceived, self).create(vals)

    """ Methods """

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
