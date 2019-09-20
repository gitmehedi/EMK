from odoo import fields, models

class ChequePaymentLine(models.Model):
    _name = 'cheque.payment.line.layer'
    _description = 'DO Cash Payment line'

    number = fields.Char("Cheque No.")
    bank = fields.Char("Deposit Bank")
    branch = fields.Char("Branch")
    amount = fields.Float("Amount")
    payment_date = fields.Date('Date')
    account_payment_id = fields.Many2one('account.payment', string='Payment Information')

    """ Relational Fields """
    pay_cash_id = fields.Many2one('delivery.order', ondelete='cascade')


