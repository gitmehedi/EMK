from odoo import models, fields, api, _


class InheritedAccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_narration = fields.Text(string='Narration', readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')

    @api.onchange('payment_narration')
    def onchange_narration(self):
        if self.payment_narration:
            self.payment_narration = self.payment_narration.strip()

    def _get_counterpart_move_line_vals(self, invoice=False):
        res = super(InheritedAccountPayment, self)._get_counterpart_move_line_vals(self.invoice_ids)
        if self.payment_narration and len(self.payment_narration.strip()) > 0:
            res['name'] = self.payment_narration.strip()

        return res
