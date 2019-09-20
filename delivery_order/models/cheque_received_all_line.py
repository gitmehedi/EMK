from odoo import fields, models

class ChequePaymentLine(models.Model):
    _name = 'cheque.entry.line'
    _description = 'All Cheque Entry Line'

    number = fields.Char("Cheque No.")
    bank = fields.Char("Deposit Bank")
    branch = fields.Char("Branch")
    amount = fields.Float("Amount")
    payment_date = fields.Date('Date')
    account_payment_id = fields.Many2one('account.payment', string='Online Payment Information')
    cheque_info_id = fields.Integer(string='Cheque Info')

    currency_id = fields.Many2one('res.currency', string='Currency')

    """ Relational Fields """
    pay_all_cq_id = fields.Many2one('delivery.authorization', ondelete='cascade')
    state = fields.Char(string='State')

    converted_amount = fields.Float(string='Converted amount')



