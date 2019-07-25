from odoo import api, fields, models, _


class BeneficiaryCertificate(models.AbstractModel):
    _name = 'report.lc_sales_product_foreign.report_certificate_origin'

    @api.multi
    def render_html(self, docids, data=None):
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.browse(data.get('shipment_id'))
        report_utility_pool = self.env['report.utility']
        qty_list = []
        prod_list = []

        address = shipment_obj.lc_id.second_party_applicant.address_get(['delivery', 'invoice'])
        delivery_address = self.env['res.partner'].browse(address['delivery'])
        invoice_address = self.env['res.partner'].browse(address['invoice'])

        data = {
            'delivery_address': report_utility_pool.getCoustomerAddress(delivery_address),
            'invoice_address': report_utility_pool.getCoustomerAddress(invoice_address),
            'first_party': shipment_obj.lc_id.first_party.name,
            'lc_id': shipment_obj.lc_id.unrevisioned_name,
            'lc_date': report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(shipment_obj.lc_id.issue_date)),
            'second_party_bank': shipment_obj.lc_id.second_party_bank,
            'invoice_number_dummy': shipment_obj.invoice_number_dummy,
            'invoice_date_dummy': shipment_obj.invoice_date_dummy,
            'count_qty': shipment_obj.count_qty,
            'count_uom': shipment_obj.count_uom.name,
            'discharge_port': shipment_obj.lc_id.discharge_port,
            'discharge_port_country_id': shipment_obj.lc_id.discharge_port_country_id.name,
            'landing_port': shipment_obj.lc_id.landing_port,
            'landing_port_country_id': shipment_obj.lc_id.landing_port_country_id.name,
            'currency_id': shipment_obj.lc_id.currency_id.name,
            'second_party_applicant': shipment_obj.lc_id.second_party_applicant.name,
            'truck_receipt_no': shipment_obj.truck_receipt_no,
            'model_type': shipment_obj.lc_id.model_type,
            'sc_type': shipment_obj.lc_id.sc_type,
            'bl_date': shipment_obj.bl_date
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
                    'total_price': prod_line.product_qty * prod_line.price_unit}
                qty_list.append(prod['quantity'])
                uom.append(prod['uom'])
                prod_list.append(prod)

        pi_list = []
        pack_list = []
        if shipment_obj.lc_id.pi_ids_temp:
            for pi in shipment_obj.lc_id.pi_ids_temp[0]:
                pack = {'pack_type': pi.pack_type.display_name}
                pack_list.append(pack)
            for pi in shipment_obj.lc_id.pi_ids_temp:
                pi_obj = {}
                pi_obj['number'] = pi.name
                pi_obj['date'] = report_utility_pool.getERPDateFormat(
                    report_utility_pool.getDateFromStr(pi.invoice_date))
                pi_list.append(pi_obj)


        total_qty = sum(qty_list)

        docargs = {
            'data': data,
            'lists': prod_list,
            'total_qty': total_qty,
            'uom': uom[0] if len(uom) > 0 else 0,
            'pi_list': pi_list,
            'pack_list': pack_list,
        }

        return self.env['report'].render('lc_sales_product_foreign.report_certificate_origin', docargs)
