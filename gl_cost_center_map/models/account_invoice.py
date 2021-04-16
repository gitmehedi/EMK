from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def register_payment(self, payment_line, writeoff_acc_id=False, writeoff_journal_id=False):
        """ Sent cost center with context """
        if self:
            self.env.context = dict(self.env.context)
            self.env.context.update({'cost_center_id': self.invoice_line_ids[0].product_id.cost_center_id.id})

        return super(AccountInvoice, self).register_payment(payment_line, writeoff_acc_id, writeoff_journal_id)
