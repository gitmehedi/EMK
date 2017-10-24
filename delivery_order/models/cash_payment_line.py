from odoo import api, fields, models

class CashPaymentLine(models.Model):
    _name = 'cash.payment.line'
    _description = 'Cash Payment Terms line'

    dep_bank = fields.Char(string="Deposited Bank")
    branch = fields.Char(string="Branch")
    validity = fields.Integer(string="Validity (Days)")
    account_payment_id = fields.Many2one('account.payment', string='Payment Information')
    amount = fields.Float(string="Amount")

    """ Relational Fields """
    pay_cash_id = fields.Many2one('delivery.order', ondelete='cascade')
