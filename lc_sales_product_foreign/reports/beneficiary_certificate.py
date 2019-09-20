from odoo import api, fields, models, _
from odoo.tools.misc import formatLang



class BeneficiaryCertificate(models.AbstractModel):
    _name = 'report.lc_sales_product_foreign.report_beneficiary_certificate'

    @api.multi
    def render_html(self, docids, data=None):
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.browse(data.get('shipment_id'))
        report_utility_pool = self.env['report.utility']
        qty_list = []
        prod_list = []
        address = shipment_obj.lc_id.second_party_applicant.address_get(['delivery', 'invoice'])
        invoice_address = self.env['res.partner'].browse(address['invoice'])
        lc_clause = data['lc_clause']
        data = {
            'lc_clause': lc_clause,
            'insurance_company_name': shipment_obj.lc_id.insurance_company_name,
            'insurance_company_address': shipment_obj.lc_id.insurance_company_address,
            'insurance_number': shipment_obj.lc_id.insurance_number,
            'insurance_policy_date': shipment_obj.lc_id.insurance_policy_date,
            'trans_shipment': shipment_obj.lc_id.trans_shipment,
            'lc_id': shipment_obj.lc_id.unrevisioned_name,
            'issue_date': report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(shipment_obj.lc_id.issue_date)),
            'second_party_bank': shipment_obj.lc_id.second_party_bank,
            'partial_shipment': shipment_obj.lc_id.partial_shipment,
            'shipment_number': shipment_obj.name,
            'container_no': shipment_obj.container_no,
            'mother_vessel': shipment_obj.mother_vessel,
            'vehical_no': shipment_obj.vehical_no,
            'etd_date': shipment_obj.etd_date,
            'eta_date': shipment_obj.eta_date,
            'etd_trans_shipment_date': shipment_obj.etd_trans_shipment_date,
            'eta_trans_shipment_date': shipment_obj.eta_trans_shipment_date,
            'second_party_applicant': shipment_obj.lc_id.second_party_applicant.name,
            'invoice_address': report_utility_pool.getCoustomerAddress(invoice_address),
            'first_party': shipment_obj.lc_id.first_party.name,
            'model_type': shipment_obj.lc_id.model_type,
            'sc_type': shipment_obj.lc_id.sc_type,
            'truck_receipt_no': shipment_obj.truck_receipt_no,
            'bl_date': shipment_obj.bl_date,
            'landing_port': shipment_obj.lc_id.landing_port,
            'landing_port_country_id': shipment_obj.lc_id.landing_port_country_id.name,
            'transshipment_country_id': shipment_obj.lc_id.transshipment_country_id.name,
            'discharge_port': shipment_obj.lc_id.discharge_port,
            'discharge_port_country_id': shipment_obj.lc_id.discharge_port_country_id.name,
            'gross_weight': formatLang(self.env, shipment_obj.gross_weight),
            'net_weight': formatLang(self.env, shipment_obj.net_weight),

        }




        uom = []
        if shipment_obj.shipment_product_lines:
            for prod_line in shipment_obj.shipment_product_lines:
                prod = {
                'name': prod_line.product_id.name_get()[0][1],
                'hs_code': prod_line.product_id.hs_code_id.display_name,
                'quantity': prod_line.product_qty,
                'unit_price': prod_line.price_unit,
                'uom': prod_line.product_uom.name,
                'total_price': prod_line.product_qty * prod_line.price_unit
                }
                qty_list.append(prod['quantity'])
                uom.append(prod['uom'])
                prod_list.append(prod)

        pi_list = []
        if shipment_obj.lc_id.pi_ids_temp:
            for pi in shipment_obj.lc_id.pi_ids_temp:
                pi_obj = {}
                pi_obj['number'] = pi.name
                pi_obj['date'] = report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(pi.invoice_date))
                pi_list.append(pi_obj)


        total_qty = sum(qty_list)


        docargs = {
            'data': data,
            'lists': prod_list,
            'total_qty': total_qty,
            'uom': uom[0] if len(uom)>0 else 0,
            'pi_list': pi_list,
        }

        return self.env['report'].render('lc_sales_product_foreign.report_beneficiary_certificate', docargs)
