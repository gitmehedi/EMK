from openerp import api, fields, models, exceptions, _

class MrpDailyProductionLine(models.Model):
    _name = 'cash.payment.line'
    _description = 'Cash Payment Terms line'

    amount = fields.Float("Amount")
    dep_bank = fields.Char("Deposited Bank")
    branch = fields.Char("Branch")
    validity = fields.Float("Validity(Days)")
    """ Relational Fields """
    pay_cash_id = fields.Many2one('delivery.order', ondelete='cascade')


