from odoo import models, fields


class InheriteAccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    cheque_received_id = fields.Many2one('accounting.cheque.received', string='Cheque Received ID')

