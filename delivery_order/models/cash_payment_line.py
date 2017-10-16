from odoo import fields, models

class CashPaymentLine(models.Model):
    _name = 'cash.payment.line'
    _description = 'Cash Payment Terms line'

    amount = fields.Float(string="Amount")
    dep_bank = fields.Char(string="Deposited Bank")
    branch = fields.Char(string="Branch")
    validity = fields.Float(string="Validity(Days)")
    account_payment_id = fields.Many2one('account.payment', string='Payment Information')

    """ Relational Fields """
    pay_cash_id = fields.Many2one('delivery.order', ondelete='cascade')




