from odoo import api, exceptions, fields, models

class GbsProformaInvoice(models.AbstractModel):
    _name = 'report.gbs_pi_creation.report_proforma_invoice'

    @api.multi
    def render_html(self, docids, data=None):
        pi_obj = self.env['proforma.invoice'].browse(docids[0])
        report_utility_pool = self.env['report.utility']

        total_amount = []
        line_list = []
        data = {}
        data['name'] = pi_obj.name
        data['pi_date'] = pi_obj.invoice_date
        data['beneficiary_id'] = pi_obj.beneficiary_id.name
        data['vat'] = pi_obj.operating_unit_id.partner_id.vat
        data['customer'] = pi_obj.partner_id.name
        data['customer_add'] = report_utility_pool.getCoustomerInvoiceAddress(pi_obj.partner_id)
        data['transport_by'] = pi_obj.transport_by
        data['terms_condition'] = pi_obj.terms_condition
        data['advising_bank'] = pi_obj.advising_bank
        data['packing'] = pi_obj.packing
        data['terms_of_payment'] = pi_obj.terms_of_payment
        data['unit_address'] = report_utility_pool.getAddressByUnit(pi_obj.operating_unit_id)


        if pi_obj.line_ids:
            for line in pi_obj.line_ids:
                list_obj = {}
                list_obj['product_id']= line.product_id.name
                list_obj['quantity']= line.quantity
                list_obj['price_unit']= line.price_unit
                list_obj['price_subtotal']= line.price_subtotal
                total_amount.append(list_obj['price_subtotal'])
                line_list.append(list_obj)

        total = sum(total_amount)
        amt_to_word = self.env['res.currency'].amount_to_word(float(total))


        docargs = {
            'data': data,
            'line_list':line_list,
            'total_amount': total,
            'amt_to_word': amt_to_word,
        }

        return self.env['report'].render('gbs_pi_creation.report_proforma_invoice', docargs)