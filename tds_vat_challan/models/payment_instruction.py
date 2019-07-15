from odoo import models, fields, api, _


class PaymentInstruction(models.Model):
    _inherit = 'payment.instruction'

    is_tax = fields.Boolean(string="Is TDS/VAT",copy=False,default=False)
    account_move_line_ids = fields.Many2many('account.move.line', 'payment_move_line_rel', 'payment_id', 'move_line_id',
                                   string='Payment Move Lines')

    @api.multi
    def action_approve(self):
        if self.is_tax:
            self.account_move_line_ids.write({'is_paid':True})
        return super(PaymentInstruction, self).action_approve()