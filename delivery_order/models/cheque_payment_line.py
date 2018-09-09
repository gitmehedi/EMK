from odoo import fields, models

class ChequePaymentLine(models.Model):
    _name = 'cheque.payment.line'
    _description = 'Cash Cheque Payment line'

    number = fields.Char("Cheque No.")
    bank = fields.Char("Deposit Bank")
    branch = fields.Char("Branch")
    amount = fields.Float("Amount")
    payment_date = fields.Date('Date')
    account_payment_id = fields.Many2one('account.payment', string='Online Payment Information')
    cheque_info_id = fields.Integer(string='Cheque Info')

    currency_id = fields.Many2one('res.currency', string='Currency')

    """ Relational Fields """
    pay_cash_id = fields.Many2one('delivery.authorization', ondelete='cascade')


