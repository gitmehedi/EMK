from . import test_account_tax as test_at
from config import CASE_VAT_SELECTION, CASE_LINE, CASE_RESULT

VAT_SELECTION = {
    'General': 'normal',
    'Mushok-6.3': 'mushok',
    'VDS Authority': 'vds_authority'
}


class TestInvoiceTax(test_at.TestAccountTax):

    def test_create_invoice_validate(self):

        for index in CASE_LINE:
            print("####################### CASE : " + str(index) + " #######################")

            selection = VAT_SELECTION['General'] if index not in CASE_VAT_SELECTION else VAT_SELECTION[CASE_VAT_SELECTION[index]]
            lines = CASE_LINE[index]

            invoice = self.env['account.invoice'].sudo(self.user_id.id).create(self._prepare_invoice(selection, lines))
            self.assertEqual(round(invoice.amount_untaxed, 2), CASE_RESULT[index]['amount_untaxed'])
            self.assertEqual(round(invoice.amount_tax, 2), CASE_RESULT[index]['amount_tax'])
            self.assertEqual(round(invoice.amount_total, 2), CASE_RESULT[index]['amount_total'])
            self.assertEqual(round(invoice.amount_tds, 2), CASE_RESULT[index]['amount_tds'])
            self.assertEqual(round(invoice.amount_vat_payable, 2), CASE_RESULT[index]['amount_vat_payable'])

            print("STATUS: PASS")

        print ("\n####################### TEST COMPLETED #######################")
