from odoo import fields, models

class LCPaymentLine(models.Model):
    _name = 'lc.payment.line'
    _description = 'L/C Payment Terms line'

    number = fields.Integer("Number")
    bank = fields.Char("Bank")
    branch = fields.Char("Branch")
    amount = fields.Float("Amount")
    date = fields.Date('Date')
    pi_id = fields.Integer("PI No")
    """ Relational Fields """
    pay_lc_id = fields.Many2one('delivery.order', ondelete='cascade')

    lc_type = fields.Selection([
        ('local', 'Local TK'),
        ('back', 'Back to Back'),
        ('bond', 'Bond'),
        ('export', 'Export'),
    ], string='L/C Type')

    transportation = fields.Selection([
        ('cf', 'C&F'),
        ('fob', 'FOB'),
    ], string='Transportation')

    tenure = fields.Selection([
        ('sight', 'At Sight'),
        ('90days', '90 Days'),
        ('120days', '120 Days'),
        ('others', 'Others'),
    ], string='Tenure')