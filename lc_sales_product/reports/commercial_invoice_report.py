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

        data['company_id'] = shipment_obj.company_id.name
        data['factory'] = shipment_obj.company_id.street +  shipment_obj.company_id.street2
        data['buyer'] = shipment_obj.lc_id.second_party_beneficiary.name
        data['invoice_id'] = 'Dummy'
        data['invoice_date'] = 'Dummy'
        #data['buyer_address'] = report_utility_pool.getBankAddress(shipment_obj.lc_id.second_party_beneficiary)
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

        #amt_to_word = self.env['res.currency'].amount_to_word(float(prod_list.get('total_price')))


        docargs = {
            'data': data,
            'lists': prod_list,
           # 'amt_to_word': amt_to_word,
        }

        return self.env['report'].render('lc_sales_product.report_commercial_invoice', docargs)
