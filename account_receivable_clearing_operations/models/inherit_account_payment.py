from odoo import api, fields, models,_


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
                if self.partner_type == 'customer' and self.payment_type == 'inbound':
                    self.destination_account_id = credit_account.id


    # Overriding Lable for Credit account
    # def _get_counterpart_move_line_vals(self, invoice=False):
    #     res = super(InheritAccountPayment, self)._get_counterpart_move_line_vals(invoice=invoice)
    #
    #     if self.partner_type == 'customer':
    #         if self.payment_type == 'inbound':
    #             self.name = self.sale_order_id.name
    #
    #     return res
    #
    # def _get_move_vals(self, journal=None):
    #     super(InheritAccountPayment, self)._get_move_vals(journal=journal)
    #     return {'name':'rabbi'}