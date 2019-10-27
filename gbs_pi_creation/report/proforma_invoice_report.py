from odoo import api, exceptions, fields, models
from odoo.tools.misc import formatLang


class GbsProformaInvoice(models.AbstractModel):
    _name = 'report.gbs_pi_creation.report_proforma_invoice'

    @api.multi
    def render_html(self, docids, data=None):
        pi_obj = self.env['proforma.invoice'].browse(docids[0])
        report_utility_pool = self.env['report.utility']

        total_amount = []
        line_list = []
        data = {}

        address = pi_obj.partner_id.address_get(['delivery', 'invoice'])
        customer = self.env['res.partner'].browse(address['delivery'])

        data['name'] = pi_obj.name
        data['region_type'] = pi_obj.region_type
        data['pi_date'] = report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(pi_obj.invoice_date))
        data['beneficiary_id'] = pi_obj.beneficiary_id.name
        data['vat'] = pi_obj.operating_unit_id.partner_id.vat
        data['bin'] = pi_obj.operating_unit_id.partner_id.bin
        data['customer'] = pi_obj.partner_id.name
        data['customer_add'] = report_utility_pool.getCoustomerAddress(customer)
        data['ntn_no'] = customer.ntn_no
        data['gst_no'] = customer.gst_no
        data['iec_no'] = customer.iec_no
        data['transport_by'] = pi_obj.transport_by
        data['terms_condition'] = pi_obj.terms_condition
        data['advising_bank'] = pi_obj.advising_bank_acc_id.bank_id.name
        data['bank_add'] = report_utility_pool.getBranchAddress(pi_obj.advising_bank_acc_id)
        data['acc_number'] = pi_obj.advising_bank_acc_id.acc_number
        data['swift_code'] = pi_obj.advising_bank_acc_id.bank_swift_code
        data['currency'] = pi_obj.currency_id.name
        data['packing'] = pi_obj.pack_type.packaging_mode

        if pi_obj.region_type == 'foreign' and pi_obj.account_payment_term_id and pi_obj.account_payment_term_id.name:
            data['terms_str'] = pi_obj.account_payment_term_id.name
        else:
            data['terms_str'] = "By Equivalent Letter Of Credit"

        data['terms_of_delivery'] = pi_obj.terms_of_delivery

        data['unit_address'] = report_utility_pool.getAddressByUnit(pi_obj.operating_unit_id)


        if pi_obj.line_ids:
            for line in pi_obj.line_ids:
                list_obj = {}
                list_obj['pro_name']= line.product_id.name_get()[0][1]
                list_obj['quantity']= line.quantity
                list_obj['hs_code']= line.product_id.hs_code_id.display_name
                list_obj['uom']= line.uom_id.name
                list_obj['price_unit']= formatLang(self.env,line.price_unit)
                list_obj['price_subtotal_price']= formatLang(self.env,line.price_subtotal)
                list_obj['price_subtotal']= line.price_subtotal
                total_amount.append(list_obj['price_subtotal'])
                line_list.append(list_obj)

        total= sum(total_amount)

        amt_to_word = self.env['res.currency'].amount_to_word(float(round(total, 2)),True,data['currency'])

        docargs = {
            'data': data,
            'line_list':line_list,
            'total_amount': formatLang(self.env,total),
            'amt_to_word': amt_to_word,
        }

        return self.env['report'].render('gbs_pi_creation.report_proforma_invoice', docargs)