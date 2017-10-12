from odoo import api, fields, models, exceptions, _

class MrpDailyProductionLine(models.Model):
    _name = 'cheque.payment.line'
    _description = 'Cash Payment Terms line'

    number = fields.Float("Number")
    bank = fields.Char("Bank")
    branch = fields.Char("Branch")
    amount = fields.Float("Amount")
    date = fields.Date('Date')
    """ Relational Fields """
    pay_cash_id = fields.Many2one('delivery.order', ondelete='cascade')


