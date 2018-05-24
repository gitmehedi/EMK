from odoo import api, fields, models, _


class CommercialInvoice(models.AbstractModel):
    _name = 'report.lc_sales_product.report_commercial_invoice'

    @api.multi
    def render_html(self, docids, data=None):
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.browse(data.get('lc_id'))
        report_utility_pool = self.env['report.utility']
        prod_list = []
        data = {}
        qty_list = []
        total_price_list = []

        data['company_id'] = shipment_obj.company_id.name
        data['factory'] = report_utility_pool.getAddressByUnit(shipment_obj.operating_unit_id)
        data['buyer'] = shipment_obj.lc_id.second_party_applicant.name
        data['buyer_address'] = report_utility_pool.getCoustomerAddress(shipment_obj.lc_id.second_party_applicant)
        data['invoice_id'] = shipment_obj.invoice_id.display_name
        data['invoice_date'] = shipment_obj.invoice_id.date_invoice
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

                prod_list.append(prod)

                qty_list.append(prod['quantity'])
                total_price_list.append(prod['total_price'])

        total_qty = sum(qty_list)
        total_price = sum(total_price_list)

        amt_to_word = self.env['res.currency'].amount_to_word(float(total_price))

        docargs = {
            'data': data,
            'lists': prod_list,
            'amt_to_word': amt_to_word,
            'total_qty': total_qty,
            'total_price': total_price,
        }

        return self.env['report'].render('lc_sales_product.report_commercial_invoice', docargs)
