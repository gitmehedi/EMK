from odoo import fields, models

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def print_account_invoice_vendor_bill(self):
        data = {}
        data['active_id'] = self.id
        return self.env['report'].get_action(self, 'account_reports_extend.report_vendor_bill_document', data)


    def print_account_invoice_customer_invoice(self):
        data = {}
        data['active_id'] = self.id
        return self.env['report'].get_action(self, 'account_reports_extend.report_customer_invoice_document', data)