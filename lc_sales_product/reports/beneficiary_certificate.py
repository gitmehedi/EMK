from odoo import api, fields, models, _


class BeneficiaryCertificate(models.AbstractModel):
    _name = 'report.lc_sales_product.report_beneficiary_certificate'

    @api.multi
    def render_html(self, docids, data=None):
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.browse(data.get('shipment_id'))
        report_utility_pool = self.env['report.utility']
        data = {}
        qty_list = []
        prod_list = []

        address = shipment_obj.lc_id.second_party_applicant.address_get(['delivery', 'invoice'])
        delivery_address = self.env['res.partner'].browse(address['delivery'])
        invoice_address = self.env['res.partner'].browse(address['invoice'])
        data['delivery_address'] = report_utility_pool.getCoustomerAddress(delivery_address)
        data['invoice_address'] = report_utility_pool.getCoustomerAddress(invoice_address)
        data['first_party'] = shipment_obj.lc_id.first_party.name
        data['factory'] = report_utility_pool.getAddressByUnit(shipment_obj.operating_unit_id)
        data['buyer'] = shipment_obj.lc_id.second_party_applicant.name
        data['buyer_address'] = report_utility_pool.getCoustomerAddress(shipment_obj.lc_id.second_party_applicant)
        data['invoice_id'] = shipment_obj.invoice_id.display_name
        data['invoice_date'] = report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(shipment_obj.invoice_id.date_invoice))
        data['arrival_date'] = report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(shipment_obj.arrival_date))
        data['terms_condition'] = shipment_obj.lc_id.terms_condition
        data['pi_id'] = shipment_obj.lc_id.pi_ids_temp.name
        data['pi_date'] = shipment_obj.lc_id.pi_ids_temp.create_date
        data['lc_id'] = shipment_obj.lc_id.name
        data['lc_date'] = shipment_obj.lc_id.issue_date
        data['second_party_bank'] = shipment_obj.lc_id.second_party_bank

        if shipment_obj.lc_id.product_lines:
            for prod_line in shipment_obj.lc_id.product_lines:
                prod = {}
                prod['name'] = prod_line.product_id.name
                prod['hs_code'] = 'Dummy'
                prod['quantity'] = prod_line.product_qty
                prod['unit_price'] = prod_line.price_unit
                prod['total_price'] = prod_line.product_qty * prod_line.price_unit
                qty_list.append(prod['quantity'])
                prod_list.append(prod)

        total_qty = sum(qty_list)

        docargs = {
            'data': data,
            'lists': prod_list,
            'total_qty': total_qty,
        }

        return self.env['report'].render('lc_sales_product.report_beneficiary_certificate', docargs)
