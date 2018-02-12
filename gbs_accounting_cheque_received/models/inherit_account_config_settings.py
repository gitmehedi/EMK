from odoo import models, fields, api


class MoneyReceiptSequence(models.TransientModel):
    _inherit = 'account.config.settings'
    
    # @api.multi
    # def _default_money_receipt_seq_id(self):
    #     for acc in self:
    #         acc_conf_sett_pool = acc.env['account.config.settings'].search([], order='id desc', limit=1)
    #         acc.money_receipt_seq_id = acc_conf_sett_pool.money_receipt_seq_id.id


    money_receipt_seq_id = fields.Many2one('account.money.receipt', help='Money Receipt Seq- allows to generate unique sequences for Cash and Cheque section',
                                           )
    #default = lambda self: self._default_money_receipt_seq_id()
