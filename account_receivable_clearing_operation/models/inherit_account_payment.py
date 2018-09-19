from odoo import api, fields, models, _


class InheritAccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):

        super(InheritAccountPayment, self)._compute_destination_account_id()

        if self.company_id and self.company_id.account_receive_clearing_acc:
            if self.partner_type == 'customer' and self.payment_type == 'inbound':
                self.destination_account_id = self.company_id.account_receive_clearing_acc.id
