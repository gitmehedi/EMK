from odoo import models, fields, api, _


class InheritedAccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_narration = fields.Text(string='Narration', readonly=True, states={'draft': [('readonly', False)]},
                                    track_visibility='onchange')

    @api.onchange('payment_narration')
    def onchange_narration(self):
        if self.payment_narration:
            self.payment_narration = self.payment_narration.strip()

    def _get_counterpart_move_line_vals(self, invoice=False):
        res = super(InheritedAccountPayment, self)._get_counterpart_move_line_vals(self.invoice_ids)
        if self.payment_narration and len(self.payment_narration.strip()) > 0:
            res['name'] = self.payment_narration.strip()

        return res

    def action_cheque_print(self):
        obj = self.env['cheque.print.wizard'].create(
            {'amount': self.amount, 'pay_to': self.partner_id.name, 'date_on_cheque': self.payment_date,
             'amount_in_word': self.check_amount_in_words})

        return {
            'name': _('Cheque Print'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'cheque.print.wizard',
            'context': {'from_payment': True,
                        'journal_id': self.journal_id.id,
                        'payment_method_id': self.payment_method_id.id,
                        'amount': self.amount,
                        'currency_id': self.currency_id.id,
                        'payment_date': self.payment_date,
                        'communication': self.communication,
                        'payment_narration': self.payment_narration},
            'res_id': obj.id,
            'nodestroy': True,
            'target': 'new'
        }
