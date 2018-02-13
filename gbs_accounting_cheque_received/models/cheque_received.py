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
        for cr in self:
            acc_move_line_pool = cr.env['account.move.line']
            account_move = cr.env['account.move']

            move_vals = {}
            move_vals['name'] = 'test' #@todo: Need this in a shape like this: "BNK1/2018/0008"
            move_vals['date'] = cr.date_on_cheque
            move_vals['company_id'] = cr.company_id.id
            move_vals['journal_id'] = cr.company_id.bank_journal_ids.id
            move_vals['partner_id'] = cr.partner_id.id
            move_vals['state'] = 'posted'
            #move_vals['payment_id'] = cr.id

            account_move.create(move_vals)

            move_line_vals = {}
            move_line_vals['partner_id'] = cr.partner_id.id

            # move_line_vals['payment_id'] =
            move_line_vals['invoice_id'] = False
            # move_line_vals['currency_id'] = False
            move_line_vals['credit'] = cr.cheque_amount
            move_line_vals['debit'] = cr.cheque_amount
            # move_line_vals['operating_unit_id'] =
            # move_line_vals['amount_currency'] =
            move_line_vals['move_id'] = cr.id
            move_line_vals['date_maturity'] = cr.date_on_cheque
            move_line_vals['name'] = 'test2' #@todo: Need to change it

            if move_line_vals['credit']:
                move_line_vals['account_id'] = cr.company_id.bank_journal_ids.default_debit_account_id.id
                move_line_vals['debit'] = 0.00

                acc_move_line_pool.create(move_line_vals)

            if move_vals['debit']:
                move_line_vals['account_id'] = cr.partner_id.property_account_receivable_id.id
                move_line_vals['credit'] = 0.00

                acc_move_line_pool.create(move_line_vals)

            cr.state = 'honoured'


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
