from odoo import api, fields, models, _
from odoo.tools.misc import formatLang
import re

class CommercialInvoice(models.AbstractModel):
    _name = 'report.lc_sales_product_foreign.report_commercial_invoice'

    @api.multi
    def render_html(self, docids, data=None):
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.browse(data.get('lc_id'))
        report_utility_pool = self.env['report.utility']
        prod_list = []
        qty_list = []
        total_price_list = []
        pi_id_list = []
        lc_revision_list = []
        data = {
            'ntn_no': shipment_obj.lc_id.second_party_applicant.ntn_no,
            'iec_no': shipment_obj.lc_id.second_party_applicant.iec_no,
            'gst_no': shipment_obj.lc_id.second_party_applicant.gst_no,
            'discharge_port': shipment_obj.lc_id.discharge_port,
            'discharge_port_country_id': shipment_obj.lc_id.discharge_port_country_id.name,
            'landing_port': shipment_obj.lc_id.landing_port,
            'landing_port_country_id': shipment_obj.lc_id.landing_port_country_id.name,
            'payment_terms': shipment_obj.lc_id.payment_terms,
            'declaration': shipment_obj.lc_id.declaration,
            'model_type': shipment_obj.lc_id.model_type,
            'sc_type': shipment_obj.lc_id.sc_type,
            'is_seaworthy_packing': shipment_obj.lc_id.is_seaworthy_packing,
            'shipment_number': shipment_obj.name,
            'cover_note_no': shipment_obj.lc_id.cover_note_no,
            'insurance_date': shipment_obj.lc_id.insurance_date,
            'insurance_number': shipment_obj.lc_id.insurance_number,
            'insurance_policy_date': shipment_obj.lc_id.insurance_policy_date,
            'truck_receipt_no': shipment_obj.truck_receipt_no,
            'bl_date': shipment_obj.bl_date,
            'invoice_number_dummy': shipment_obj.invoice_number_dummy,
            'invoice_date_dummy': shipment_obj.invoice_date_dummy,
            'invoice_value': shipment_obj.invoice_value,
            'is_print_cfr': shipment_obj.is_print_cfr,
            'fob_value': shipment_obj.fob_value,
            'feright_value': shipment_obj.feright_value,
            'company_id': shipment_obj.company_id.name,
            'factory': report_utility_pool.getAddressByUnit(shipment_obj.operating_unit_id),
            'buyer': shipment_obj.lc_id.second_party_applicant.name,
            'buyer_address': report_utility_pool.getCoustomerAddress(shipment_obj.lc_id.second_party_applicant),
            'lc_id': shipment_obj.lc_id.unrevisioned_name,
            'lc_date': report_utility_pool.getERPDateFormat(
                report_utility_pool.getDateFromStr(shipment_obj.lc_id.issue_date)),
            'second_party_bank': shipment_obj.lc_id.second_party_bank,
            'currency_id': shipment_obj.lc_id.currency_id.name,
        }

        clean = re.compile('<.*?>')
        cylinder_details_text = re.sub(clean, '', shipment_obj.cylinder_details)

        if cylinder_details_text:
            data['cylinder_details'] = shipment_obj.cylinder_details
        else:
            data['cylinder_details'] = ""

        for pi_id in shipment_obj.lc_id.pi_ids:
            pi_id_list.append({'pi_id': pi_id.name, 'pack_type': pi_id.pack_type.display_name,
                               'pi_date': report_utility_pool.getERPDateFormat(
                                   report_utility_pool.getDateFromStr(pi_id.invoice_date))})

        for revision in shipment_obj.lc_id.old_revision_ids:
            lc_revision_list.append({'no': revision.revision_number + 1, 'date': report_utility_pool.getERPDateFormat(
                report_utility_pool.getDateFromStr(revision.amendment_date))})

        if shipment_obj.shipment_product_lines:
            for prod_line in shipment_obj.shipment_product_lines:
                prod = {
                    'name': prod_line.product_id.name_get()[0][1],
                    'hs_code': prod_line.product_id.hs_code_id.display_name,
                    'quantity': prod_line.product_qty,
                    'product_uom': prod_line.product_uom.name,
                    'unit_price': formatLang(self.env, prod_line.price_unit),
                    'sub_total_price': formatLang(self.env, prod_line.product_qty * prod_line.price_unit),
                    'total_price': prod_line.product_qty * prod_line.price_unit
                }
                prod_list.append(prod)

                qty_list.append(prod['quantity'])
                total_price_list.append(prod['total_price'])

        total_qty = sum(qty_list)
        total_price = sum(total_price_list)

        amt_to_word = self.env['res.currency'].amount_to_word(float(total_price), False)

        docargs = {
            'data': data,
            'lists': prod_list,
            'amt_to_word': amt_to_word,
            'total_qty': formatLang(self.env, total_qty),
            'total_price': formatLang(self.env, total_price),
            'pi_id_list': pi_id_list,
            'lc_revision_list': lc_revision_list
        }

        return self.env['report'].render('lc_sales_product_foreign.report_commercial_invoice', docargs)
