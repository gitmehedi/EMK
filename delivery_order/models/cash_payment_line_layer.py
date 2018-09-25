from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class CashPaymentLine(models.Model):
    _name = 'cash.payment.line.layer'
    _description = 'DO Cash Payment line'

    dep_bank = fields.Char(string="Deposited Bank")
    branch = fields.Char(string="Branch")
    validity = fields.Integer(string="Validity (Days)")
    account_payment_id = fields.Many2one('account.payment', string='Payment Information')
    amount = fields.Float(string="Amount")
    payment_date = fields.Date('Date')

    """ Relational Fields """
    pay_cash_id = fields.Many2one('delivery.order', ondelete='cascade')

    # @api.constrains('amount')
    # def check_amount(self):
    #     if self.amount <= 0.00:
    #         raise ValidationError('Amount can not be zero or negative')

    # @api.constrains('validity')
    # def check_validity(self):
    #     if self.validity <= 0.00:
    #         raise ValidationError('Validity can not be zero or negative')
