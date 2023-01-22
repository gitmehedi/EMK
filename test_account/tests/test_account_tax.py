import datetime
from odoo.tests import TransactionCase


class TestAccountTax(TransactionCase):

    def setUp(self):
        super(TestAccountTax, self).setUp()
        self.user_id = self.env['res.users'].search([('id', '=', 1)])
        self.partner_id = self.env['res.partner'].search([], limit=1)
        self.ou_id = self.env['operating.unit'].search([('code', '=', '001')])
        self.journal_id = self.env['account.journal'].search([('code', '=', 'VB')])
        self.product_id = self.env['product.product'].search([], limit=1)
        self.aaa_id = self.env['account.analytic.account'].search([('code', '=', '101')])
        self.date_invoice = self.get_date_invoice()

    def _prepare_invoice(self, vat_selection, line_products):
        lines = []
        for lp in line_products:
            vat_id = self.env['account.tax'].search([('name', '=like', lp['vat_name']), ('is_vat', '=', True), ('active', '=', True)])
            tds_id = self.env['account.tax'].search([('name', '=like', lp['tds_name']), ('is_tds', '=', True), ('active', '=', True)])

            invoice_line_tax_ids = []
            if vat_id.id:
                invoice_line_tax_ids.append((4, vat_id.id))
            if tds_id.id:
                invoice_line_tax_ids.append((4, tds_id.id))

            line_vals = {
                'product_id': self.product_id.id,
                'name': self.product_id.name,
                'account_id': self.product_id.property_account_expense_id.id,
                'sub_operating_unit_id': self.product_id.sub_operating_unit_id.id,
                'operating_unit_id': self.ou_id.id,
                'account_analytic_id': self.aaa_id.id,
                'quantity': lp['qty'],
                'price_unit': lp['unit_price'],
                'vat_id': vat_id.id,
                'tds_id': tds_id.id,
                'invoice_line_tax_ids': invoice_line_tax_ids
            }
            lines.append((0, 0, line_vals))

        inv_vals = {
            'partner_id': self.partner_id.id,
            'date_invoice': self.date_invoice,
            'vat_selection': vat_selection,
            'operating_unit_id': self.ou_id.id,
            'journal_id': self.journal_id.id,
            'account_id': self.partner_id.property_account_payable_id.id,
            'type': 'in_invoice',
            'invoice_line_ids': lines,
        }

        return inv_vals

    @staticmethod
    def get_date_invoice():
        current_date = datetime.datetime.now()
        date_str = str(current_date.year) + '-' + str(current_date.month) + '-' + str(current_date.day)
        return date_str
