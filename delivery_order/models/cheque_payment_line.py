from odoo import fields, models

class ChequePaymentLine(models.Model):
    _name = 'cheque.payment.line'
    _description = 'Cash Cheque Payment line'

    number = fields.Char("Cheque No.")
    bank = fields.Char("Deposit Bank")
    branch = fields.Char("Branch")
    payment_date = fields.Date('Date')
    account_payment_id = fields.Many2one('account.payment', string='Online Payment Information')
    cheque_info_id = fields.Integer(string='Cheque Info')

    # JOurnal related info showing
    currency_id = fields.Many2one('res.currency', string='Currency')  # Company Currency
    amount_currency = fields.Many2one('res.currency', string='Currency')  # Journal Currency
    amount_in_diff_currency = fields.Float(string='Amount in diff Currency')
    amount = fields.Float(string="Amount")  # Converted amount

    """ Relational Fields """
    pay_cash_id = fields.Many2one('delivery.authorization', ondelete='cascade')


