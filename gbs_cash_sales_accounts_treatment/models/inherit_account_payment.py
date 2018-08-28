from odoo import api, fields, models,_


class InheritAccountPayment(models.Model):
    _inherit = 'account.payment'

    sale_order_type = fields.Char(string='Sale Order Type')

    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):

        super(InheritAccountPayment, self)._compute_destination_account_id()

        if self.sale_order_id:
            company_id = self.env['res.company']._company_default_get('gbs_cash_sales_accounts_treatment')

            credit_account = company_id.cash_suspense_account

            if credit_account:
                if self.sale_order_id.type_id.sale_order_type == 'cash' and self.partner_type == 'customer':
                    self.destination_account_id = credit_account.id


    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        self.sale_order_type = self.sale_order_id.type_id.sale_order_type






