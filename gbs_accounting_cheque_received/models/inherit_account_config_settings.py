from odoo import models, fields, api


class MoneyReceiptSequence(models.TransientModel):
    _inherit = 'account.config.settings'

    money_receipt_seq_id = fields.Many2one('ir.sequence', help='Money Receipt Seq- allows to generate unique sequences for Cash and Cheque section',)
