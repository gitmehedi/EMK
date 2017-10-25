from odoo import api, fields, models, exceptions, _

class ChequePaymentLine(models.Model):
    _name = 'cheque.payment.line'
    _description = 'Cash Payment Terms line'

    number = fields.Float("Cheque No.")
    bank = fields.Char("Deposit Bank")
    branch = fields.Char("Branch")
    amount = fields.Float("Amount")
    payment_date = fields.Date('Date')
    account_payment_id = fields.Many2one('account.payment', string='Payment Information')

    """ Relational Fields """
    pay_cash_id = fields.Many2one('delivery.order', ondelete='cascade')


