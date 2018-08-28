from odoo import api, fields, models


class InheritAccountPayment(models.Model):
    _inherit = 'account.payment'


    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):

        super(InheritAccountPayment, self)._compute_destination_account_id()

        if self.sale_order_id:
            company_id = self.env['res.company']._company_default_get('account_receivable_clearing_operations')

            credit_account = company_id.cash_suspense_account

            if credit_account:
                if self.partner_type == 'customer':
                    self.destination_account_id = credit_account.id

