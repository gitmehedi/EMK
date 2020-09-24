from . import test_vat_tds as test_vt
from test_vb_config import I_VS_CASE, I_CASE, I_CASE_RESULT
from test_vb_config import R_VS_CASE, R_CASE, R_CASE_RESULT
from test_vb_config import C_VS_CASE, C_CASE, C_CASE_RESULT

VAT_SELECTION = {
    'General': 'normal',
    'Mushok-6.3': 'mushok',
    'VDS Authority': 'vds_authority'
}


class TestVBVatTds(test_vt.TestVatTds):

    def test_vendor_bill_vat_tds_calc_individual(self):
        print("####################### VENDOR BILL INDIVIDUAL CASE TESTING #######################\n")

        for CASE_NO in I_CASE:
            print("####################### CASE : " + str(CASE_NO) + " #######################")

            vat_selection = VAT_SELECTION['General'] if CASE_NO not in I_VS_CASE else VAT_SELECTION[I_VS_CASE[CASE_NO]]
            lines = I_CASE[CASE_NO]

            invoice = self.env['account.invoice'].sudo(self.user_id.id).create(self._prepare_invoice(vat_selection, lines))
            self.assertEqual(round(invoice.amount_untaxed, 2), I_CASE_RESULT[CASE_NO]['amount_untaxed'], 'Incorrect Untaxed Amount')
            self.assertEqual(round(invoice.amount_tax, 2), I_CASE_RESULT[CASE_NO]['amount_tax'], 'Incorrect VAT')
            self.assertEqual(round(invoice.amount_total, 2), I_CASE_RESULT[CASE_NO]['amount_total'], 'Incorrect Total')
            self.assertEqual(round(invoice.amount_tds, 2), I_CASE_RESULT[CASE_NO]['amount_tds'], 'Incorrect TDS')
            self.assertEqual(round(invoice.amount_vat_payable, 2), I_CASE_RESULT[CASE_NO]['amount_vat_payable'], 'Incorrect VAT payable')

            print("STATUS: PASS")

        print ("\n####################### VENDOR BILL INDIVIDUAL CASE TESTING COMPLETED #######################\n")

    def test_vendor_bill_vat_tds_calc_combination(self):
        print("####################### VENDOR BILL COMBINATION CASE TESTING #######################\n")

        for CASE_NO in R_CASE:
            print("####################### CASE : " + str(CASE_NO) + " #######################")

            vat_selection = VAT_SELECTION['General'] if CASE_NO not in R_VS_CASE else VAT_SELECTION[R_VS_CASE[CASE_NO]]
            lines = R_CASE[CASE_NO]

            invoice = self.env['account.invoice'].sudo(self.user_id.id).create(self._prepare_invoice(vat_selection, lines))
            self.assertEqual(round(invoice.amount_untaxed, 2), R_CASE_RESULT[CASE_NO]['amount_untaxed'], 'Incorrect Untaxed Amount')
            self.assertEqual(round(invoice.amount_tax, 2), R_CASE_RESULT[CASE_NO]['amount_tax'], 'Incorrect VAT')
            self.assertEqual(round(invoice.amount_total, 2), R_CASE_RESULT[CASE_NO]['amount_total'], 'Incorrect Total')
            self.assertEqual(round(invoice.amount_tds, 2), R_CASE_RESULT[CASE_NO]['amount_tds'], 'Incorrect TDS')
            self.assertEqual(round(invoice.amount_vat_payable, 2), R_CASE_RESULT[CASE_NO]['amount_vat_payable'], 'Incorrect VAT payable')

            print("STATUS: PASS")

        print ("\n####################### VENDOR BILL COMBINATION CASE TESTING COMPLETED #######################\n")

    def test_vendor_bill_vat_tds_calc_complex(self):
        print("####################### VENDOR BILL COMPLEX CASE TESTING #######################\n")

        for CASE_NO in C_CASE:
            print("####################### CASE : " + str(CASE_NO) + " #######################")

            self.partner_id = self.create_partner('TEST LTD-' + str(CASE_NO))

            adjusted_advance_ids = []
            adjusted_advance = 0

            for item in C_CASE[CASE_NO]:
                if item['is_vb']:
                    vat_selection = VAT_SELECTION['General'] if CASE_NO not in C_VS_CASE else VAT_SELECTION[C_VS_CASE[CASE_NO]]
                    lines = item['vals']

                    # create a new vendor bill
                    invoice_id = self.env['account.invoice'].sudo(self.user_id.id).create(self._prepare_invoice(vat_selection, lines, adjusted_advance_ids, adjusted_advance))

                    # check whether this invoice_id need to validate or not
                    if item['is_action_validate']:
                        invoice_id.sudo(self.user_id.id).action_invoice_open()

                else:
                    # destructuring data from dictionary
                    amount = item['vals']['advance_amount']
                    vat_name = item['vals']['vat_name']
                    tds_name = item['vals']['tds_name']

                    # create a new vendor advance
                    advance_id = self.env['vendor.advance'].sudo(self.user_id.id).create(self._prepare_advance(amount, vat_name, tds_name))

                    # check whether this advance_id need to validate or not
                    if item['is_action_validate']:
                        advance_id.sudo(self.user_id.id).action_confirm()
                        advance_id.sudo(self.user_id.id).action_validate()

                        if item['is_adjusted']:
                            adjusted_advance_ids.append((4, advance_id.id))
                            adjusted_advance += advance_id.advance_amount

            self.assertEqual(round(invoice_id.amount_untaxed, 2), C_CASE_RESULT[CASE_NO]['amount_untaxed'], 'Incorrect Untaxed Amount')
            self.assertEqual(round(invoice_id.amount_tax, 2), C_CASE_RESULT[CASE_NO]['amount_tax'], 'Incorrect VAT')
            self.assertEqual(round(invoice_id.amount_total, 2), C_CASE_RESULT[CASE_NO]['amount_total'], 'Incorrect Total')
            self.assertEqual(round(invoice_id.amount_tds, 2), C_CASE_RESULT[CASE_NO]['amount_tds'], 'Incorrect TDS')
            self.assertEqual(round(invoice_id.amount_vat_payable, 2), C_CASE_RESULT[CASE_NO]['amount_vat_payable'], 'Incorrect VAT payable')

            print("STATUS: PASS")

        print ("\n####################### VENDOR BILL COMPLEX CASE TESTING COMPLETED #######################\n")
