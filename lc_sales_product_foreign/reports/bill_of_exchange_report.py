from odoo import api, fields, models, _
from odoo.tools.misc import formatLang


class BillExchangeFirst(models.AbstractModel):
    _name = 'report.lc_sales_product_foreign.report_bill_exchange'

    @api.multi
    def render_html(self, docids, data=None):
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.browse(data.get('shipment_id'))
        report_utility_pool = self.env['report.utility']
        line_list = []
        pi_id_list = []
        address = shipment_obj.lc_id.second_party_applicant.address_get(['delivery', 'invoice'])
        delivery_address = self.env['res.partner'].browse(address['delivery'])
        invoice_address = self.env['res.partner'].browse(address['invoice'])
        bill_exchange = data['bill_exchange']

        data = {
            'bill_exchange': bill_exchange,
            'delivery_address': report_utility_pool.getCoustomerAddress(delivery_address),
            'invoice_address' : report_utility_pool.getCoustomerAddress(invoice_address),
            'document_receiver_bank' : shipment_obj.lc_id.document_receiver_bank,
            'iec_no' : shipment_obj.lc_id.second_party_applicant.iec_no,
            'gst_no' : shipment_obj.lc_id.second_party_applicant.gst_no,
            'ntn_no' : shipment_obj.lc_id.second_party_applicant.ntn_no,
            'lc_id' : shipment_obj.lc_id.unrevisioned_name,
            'issue_date' : report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(shipment_obj.lc_id.issue_date)),
            'currency_id': shipment_obj.lc_id.currency_id.name,
            'invoice_value': formatLang(self.env,shipment_obj.invoice_value),
            'tenure': shipment_obj.lc_id.tenure,
            'first_party_bank': shipment_obj.lc_id.first_party_bank_acc.bank_id.name,
            'first_party_bank_add': report_utility_pool.getBranchAddress(shipment_obj.lc_id.first_party_bank_acc),
            'inco_terms': shipment_obj.lc_id.inco_terms.code,
            'landing_port': shipment_obj.lc_id.landing_port,
            'landing_port_country_id': shipment_obj.lc_id.landing_port_country_id.name,
            'discharge_port': shipment_obj.lc_id.discharge_port,
            'discharge_port_country_id': shipment_obj.lc_id.discharge_port_country_id.name,
            'cover_note_no': shipment_obj.lc_id.cover_note_no,
            'model_type': shipment_obj.lc_id.model_type,
            'sc_type': shipment_obj.lc_id.sc_type,
            'second_party_bank': shipment_obj.lc_id.second_party_bank,
            'first_party': shipment_obj.lc_id.first_party.name,
            'first_party_add': report_utility_pool.getBranchAddress(shipment_obj.lc_id.first_party),
            'second_party_applicant': shipment_obj.lc_id.second_party_applicant.name,
            'company': shipment_obj.company_id.name,
            'factory': report_utility_pool.getAddressByUnit(shipment_obj.operating_unit_id)
        }

        price =[]
        uom = []
        if shipment_obj.shipment_product_lines:
            for line in shipment_obj.shipment_product_lines:
                list_obj = {
                'name': line.product_id.name_get()[0][1],
                'quantity': line.product_qty,
                'uom': line.product_uom.name,
                'hs_code': line.product_id.hs_code_id.display_name,
                'price_unit': formatLang(self.env,line.price_unit)
                }
                price.append(list_obj['quantity'])
                uom.append(list_obj['uom'])
                line_list.append(list_obj)

        for pi_id in shipment_obj.lc_id.pi_ids:
            pi_id_list.append({'pi_id':pi_id.name,'pack_type':pi_id.pack_type.display_name,'pi_date':report_utility_pool.getERPDateFormat(report_utility_pool.getDateTimeFromStr(pi_id.create_date))})

        pi_list =[]
        if shipment_obj.lc_id.pi_ids_temp:
            for pi in shipment_obj.lc_id.pi_ids_temp:
                pi_obj = {}
                pi_obj['number'] = pi.name
                pi_obj['date'] = report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(pi.invoice_date))
                pi_list.append(pi_obj)


        price_total = sum(price)
        total= shipment_obj.invoice_value
        amt_to_word = self.env['res.currency'].amount_to_word(float(total),False)
        docargs = {
            'data': data,
            'lists': line_list,
            'price_total': price_total,
            'amt_to_word': amt_to_word,
            'pi_list': pi_list,
            'pi_id_list': pi_id_list,
            'uom': uom[0] if len(uom)>0 else 0,

        }
        return self.env['report'].render('lc_sales_product_foreign.report_bill_exchange', docargs)