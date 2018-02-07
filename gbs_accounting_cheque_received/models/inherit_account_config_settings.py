from odoo import models, fields, api


class MoneyReceiptSequence(models.TransientModel):
    _inherit = 'account.config.settings'

    money_receipt_seq_id = fields.Many2one('account.money.receipt', string='Money Receipt Seq')

