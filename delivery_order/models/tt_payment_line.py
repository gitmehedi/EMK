from odoo import fields, models

class TTPaymentLine(models.Model):
    _name = 'tt.payment.line'
    _description = 'TT Payment Terms line'

    ref_num = fields.Integer("Ref.No")
    bank = fields.Char("Bank")
    branch = fields.Char("Branch")
    amount = fields.Float("Amount")
    date = fields.Date('Date')
    """ Relational Fields """
    pay_tt_id = fields.Many2one('delivery.order', ondelete='cascade')
