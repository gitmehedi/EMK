from odoo import api, fields, models, _


class BeneficiaryCertificate(models.AbstractModel):
    _name = 'report.lc_sales_product_local.report_inspection_certificate'

    @api.multi
    def render_html(self, docids, data=None):
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.browse(data.get('shipment_id'))
        report_utility_pool = self.env['report.utility']
        data = {}
        qty_list = []
        prod_list = []
        lc_revision_list = []

        address = shipment_obj.lc_id.second_party_applicant.address_get(['delivery', 'invoice'])
        delivery_address = self.env['res.partner'].browse(address['delivery'])
        invoice_address = self.env['res.partner'].browse(address['invoice'])
        data['delivery_address'] = report_utility_pool.getCoustomerAddress(delivery_address)
        data['invoice_address'] = report_utility_pool.getCoustomerAddress(invoice_address)
        data['first_party'] = shipment_obj.lc_id.first_party.name
        data['factory'] = report_utility_pool.getAddressByUnit(shipment_obj.operating_unit_id)
        data['buyer'] = shipment_obj.lc_id.second_party_applicant.name
        data['buyer_address'] = report_utility_pool.getCoustomerAddress(shipment_obj.lc_id.second_party_applicant)
        data['invoice_id'] = "" if shipment_obj.invoice_id.id == False else shipment_obj.invoice_id.display_name
        data['invoice_date'] = "" if shipment_obj.invoice_id.id == False else report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(shipment_obj.invoice_id.date_invoice))
        data['arrival_date'] = report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(shipment_obj.arrival_date))
        data['terms_condition'] = shipment_obj.lc_id.terms_condition
        data['lc_id'] = shipment_obj.lc_id.unrevisioned_name
        data['lc_date'] =report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr( shipment_obj.lc_id.issue_date))
        data['second_party_bank'] = shipment_obj.lc_id.second_party_bank

        uom = []
        if shipment_obj.shipment_product_lines:
            for prod_line in shipment_obj.shipment_product_lines:
                prod = {}
                prod['name'] = prod_line.product_id.name_get()[0][1]
                prod['hs_code'] = prod_line.product_id.hs_code_id.display_name
                prod['quantity'] = prod_line.product_qty
                prod['unit_price'] = prod_line.price_unit
                prod['uom'] = prod_line.product_uom.name
                prod['total_price'] = prod_line.product_qty * prod_line.price_unit
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

        for revision in shipment_obj.lc_id.old_revision_ids:
            lc_revision_list.append({'no': revision.revision_number + 1, 'date': report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(revision.amendment_date))})

        total_qty = sum(qty_list)


        docargs = {
            'data': data,
            'lists': prod_list,
            'total_qty': total_qty,
            'uom': uom[0] if len(uom)>0 else 0,
            'pi_list': pi_list,
            'lc_revision_list': lc_revision_list
        }

        return self.env['report'].render('lc_sales_product_local.report_inspection_certificate', docargs)
