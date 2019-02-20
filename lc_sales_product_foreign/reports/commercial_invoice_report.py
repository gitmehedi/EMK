from odoo import api, fields, models, _
from odoo.tools.misc import formatLang


class CommercialInvoice(models.AbstractModel):
    _name = 'report.lc_sales_product_foreign.report_commercial_invoice'

    @api.multi
    def render_html(self, docids, data=None):
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.browse(data.get('lc_id'))
        report_utility_pool = self.env['report.utility']
        prod_list = []
        data = {}
        qty_list = []
        total_price_list = []
        pi_id_list = []
        lc_revision_list = []

        data['ntn_no'] = shipment_obj.lc_id.second_party_applicant.ntn_no
        data['iec_no'] = shipment_obj.lc_id.second_party_applicant.iec_no
        data['gst_no'] = shipment_obj.lc_id.second_party_applicant.gst_no
        data['discharge_port'] = shipment_obj.lc_id.discharge_port
        data['discharge_port_country_id'] = shipment_obj.lc_id.discharge_port_country_id.name
        data['landing_port'] = shipment_obj.lc_id.landing_port
        data['landing_port_country_id'] = shipment_obj.lc_id.landing_port_country_id.name
        data['payment_terms'] = shipment_obj.lc_id.payment_terms
        data['declaration'] = shipment_obj.lc_id.declaration
        data['not_for_medical_use'] = shipment_obj.lc_id.not_for_medical_use
        data['shipment_number'] = shipment_obj.name
        data['cover_note_no'] = shipment_obj.lc_id.cover_note_no
        data['insurance_date'] = report_utility_pool.getERPDateFormat(
            report_utility_pool.getDateFromStr(shipment_obj.lc_id.insurance_date))
        data['truck_receipt_no'] = shipment_obj.truck_receipt_no
        data['bl_date'] = report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(shipment_obj.bl_date))
        data['declaration'] = shipment_obj.lc_id.declaration
        data['cylinder_details'] = shipment_obj.cylinder_details
        data['invoice_number_dummy'] = shipment_obj.invoice_number_dummy
        data['invoice_value'] = shipment_obj.invoice_value
        data['is_print_cfr'] = shipment_obj.is_print_cfr
        data['fob_value'] = shipment_obj.fob_value
        data['feright_value'] = shipment_obj.feright_value
        data['company_id'] = shipment_obj.company_id.name
        data['factory'] = report_utility_pool.getAddressByUnit(shipment_obj.operating_unit_id)
        data['buyer'] = shipment_obj.lc_id.second_party_applicant.name
        data['buyer_address'] = report_utility_pool.getCoustomerAddress(shipment_obj.lc_id.second_party_applicant)
        data['lc_id'] = shipment_obj.lc_id.unrevisioned_name
        data['lc_date'] = report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(shipment_obj.lc_id.issue_date))
        data['second_party_bank'] = shipment_obj.lc_id.second_party_bank
        data['currency_id'] = shipment_obj.lc_id.currency_id.name

        for pi_id in shipment_obj.lc_id.pi_ids:
            pi_id_list.append({'pi_id':pi_id.name,'pack_type':pi_id.pack_type.display_name,'pi_date':report_utility_pool.getERPDateFormat(report_utility_pool.getDateTimeFromStr(pi_id.create_date))})


        for revision in shipment_obj.lc_id.old_revision_ids:
            lc_revision_list.append({'no': revision.revision_number + 1, 'date': report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(revision.amendment_date))})

        if shipment_obj.shipment_product_lines:
            for prod_line in shipment_obj.shipment_product_lines:
                prod = {}
                prod['name'] = prod_line.product_id.name_get()[0][1]
                prod['hs_code'] = prod_line.product_id.hs_code_id.display_name
                prod['quantity'] = prod_line.product_qty
                prod['product_uom'] = prod_line.product_uom.name
                prod['unit_price'] = formatLang(self.env,prod_line.price_unit)
                prod['sub_total_price'] = formatLang(self.env,prod_line.product_qty * prod_line.price_unit)
                prod['total_price'] = prod_line.product_qty * prod_line.price_unit

                prod_list.append(prod)

                qty_list.append(prod['quantity'])
                total_price_list.append(prod['total_price'])

        total_qty = sum(qty_list)
        total_price = sum(total_price_list)

        amt_to_word = self.env['res.currency'].amount_to_word(float(total_price),False)

        docargs = {
            'data': data,
            'lists': prod_list,
            'amt_to_word': amt_to_word,
            'total_qty': formatLang(self.env,total_qty),
            'total_price': formatLang(self.env,total_price),
            'pi_id_list': pi_id_list,
            'lc_revision_list': lc_revision_list
        }

        return self.env['report'].render('lc_sales_product_foreign.report_commercial_invoice', docargs)
