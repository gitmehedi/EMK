from . import test_vat_tds as test_vt
from test_va_config import I_CASE, I_CASE_RESULT
from test_va_config import R_CASE, R_CASE_RESULT
from test_va_config import C_CASE, C_CASE_RESULT


class TestVBVatTds(test_vt.TestVatTds):

    def test_vendor_advance_vat_tds_calc_individual(self):
        print("####################### VENDOR ADVANCE INDIVIDUAL CASE TESTING #######################\n")

        for CASE_NO in I_CASE:
            print("####################### CASE : " + str(CASE_NO) + " #######################")

            amount = I_CASE[CASE_NO]['advance_amount']
            vat_name = I_CASE[CASE_NO]['vat_name']
            tds_name = I_CASE[CASE_NO]['tds_name']

            advance_id = self.env['vendor.advance'].sudo(self.user_id.id).create(self._prepare_advance(amount, vat_name, tds_name))

            self.assertEqual(round(advance_id.vat_amount, 2), I_CASE_RESULT[CASE_NO]['vat_amount'], 'Incorrect VAT Amount')
            self.assertEqual(round(advance_id.tds_amount, 2), I_CASE_RESULT[CASE_NO]['tds_amount'], 'Incorrect TDS Amount')

            print("STATUS: PASS")

        print ("\n####################### VENDOR ADVANCE INDIVIDUAL CASE TESTING COMPLETED #######################\n")

    # def test_vendor_advance_vat_tds_calc_combination(self):
    #     print("####################### VENDOR ADVANCE COMBINATION CASE TESTING #######################\n")
    #
    #     for CASE_NO in R_CASE:
    #         print("####################### CASE : " + str(CASE_NO) + " #######################")
    #
    #         amount = R_CASE[CASE_NO]['advance_amount']
    #         vat_name = R_CASE[CASE_NO]['vat_name']
    #         tds_name = R_CASE[CASE_NO]['tds_name']
    #
    #         advance_id = self.env['vendor.advance'].sudo(self.user_id.id).create(self._prepare_advance(amount, vat_name, tds_name))
    #
    #         self.assertEqual(round(advance_id.vat_amount, 2), R_CASE_RESULT[CASE_NO]['vat_amount'], 'Incorrect VAT Amount')
    #         self.assertEqual(round(advance_id.tds_amount, 2), R_CASE_RESULT[CASE_NO]['tds_amount'], 'Incorrect TDS Amount')
    #
    #         print("STATUS: PASS")
    #
    #     print ("\n####################### VENDOR ADVANCE COMBINATION CASE TESTING COMPLETED #######################\n")

    def test_vendor_advance_vat_tds_calc_complex(self):
        print("####################### VENDOR ADVANCE COMPLEX CASE TESTING #######################\n")

        for CASE_NO in C_CASE:
            print("####################### CASE : " + str(CASE_NO) + " #######################")

            # self.partner_id = self.create_partner('TEST LTD-' + str(CASE_NO))

            for item in C_CASE[CASE_NO]:
                if item['is_vb']:
                    vat_selection = 'normal'    # For General VAT Selection
                    lines = item['vals']

                    # create a new vendor bill
                    invoice_id = self.env['account.invoice'].sudo(self.user_id.id).create(self._prepare_invoice(vat_selection, lines))

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

            self.assertEqual(round(advance_id.vat_amount, 2), C_CASE_RESULT[CASE_NO]['vat_amount'], 'Incorrect VAT Amount')
            self.assertEqual(round(advance_id.tds_amount, 2), C_CASE_RESULT[CASE_NO]['tds_amount'], 'Incorrect TDS Amount')

            print("STATUS: PASS")

        print ("\n####################### VENDOR ADVANCE COMPLEX CASE TESTING COMPLETED #######################\n")
