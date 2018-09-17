from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class CashPaymentLine(models.Model):
    _name = 'cash.payment.line'
    _description = 'Cash Payment line'

    dep_bank = fields.Char(string="Deposited Bank")
    branch = fields.Char(string="Branch")
    validity = fields.Integer(string="Validity (Days)")
    account_payment_id = fields.Char(string='Payment Information')
    payment_date = fields.Date('Date')

    # JOurnal related info showing
    currency_id = fields.Many2one('res.currency', string='Currency') # Company Currency
    amount_currency = fields.Many2one('res.currency', string='Currency') # Journal Currency
    amount_in_diff_currency = fields.Float(string='Amount in diff Currency')
    amount = fields.Float(string="Amount") #Converted amount



    """ Relational Fields """
    pay_cash_id = fields.Many2one('delivery.authorization', ondelete='cascade')

    @api.constrains('amount')
    def check_amount(self):
        if self.amount <= 0.00:
            raise ValidationError('Amount can not be zero or negative')

    # @api.constrains('validity')
    # def check_validity(self):
    #     if self.validity <= 0.00:
    #         raise ValidationError('Validity can not be zero or negative')
