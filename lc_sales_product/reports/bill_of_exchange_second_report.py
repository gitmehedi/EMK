from odoo import api, fields, models, _

class BillExchangeFirst(models.AbstractModel):
    _name = 'report.lc_sales_product.report_bill_exchange_second'

    @api.multi
    def render_html(self, docids, data=None):
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.browse(data.get('shipment_id'))
        report_utility_pool = self.env['report.utility']
        line_list = []
        data = {}
        address = shipment_obj.lc_id.second_party_applicant.address_get(['delivery', 'invoice'])
        delivery_address = self.env['res.partner'].browse(address['delivery'])
        invoice_address = self.env['res.partner'].browse(address['invoice'])
        data['delivery_address'] = report_utility_pool.getCoustomerAddress(delivery_address)
        data['invoice_address'] = report_utility_pool.getCoustomerAddress(invoice_address)
        data['first_party_bank'] = shipment_obj.lc_id.first_party_bank.name
        data['second_party_bank'] = shipment_obj.lc_id.second_party_bank
        data['first_party'] = shipment_obj.lc_id.first_party.name
        data['second_party_applicant'] = shipment_obj.lc_id.second_party_applicant.name
        data['first_party_bank_add'] = report_utility_pool.getBankAddress(shipment_obj.lc_id.first_party_bank)
        data['company'] = shipment_obj.company_id.name
        data['currency_id'] = shipment_obj.lc_id.currency_id.name
        data['invoice_value'] = shipment_obj.invoice_value
        data['invoice_id'] = shipment_obj.invoice_id.display_name
        data['invoice_date'] = report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(shipment_obj.invoice_id.date_invoice))
        data['terms_condition'] = shipment_obj.lc_id.terms_condition
        data['tenure'] = shipment_obj.lc_id.tenure
        data['lc_id'] = shipment_obj.lc_id.name
        data['issue_date'] = report_utility_pool.getERPDateFormat(
            report_utility_pool.getDateFromStr(shipment_obj.lc_id.issue_date))

        price = []
        uom = []
        if shipment_obj.shipment_product_lines:
            for line in shipment_obj.shipment_product_lines:
                list_obj = {}
                list_obj['name'] = line.product_id.name_get()[0][1]
                list_obj['quantity'] = line.product_qty
                list_obj['uom'] = line.product_uom.name
                list_obj['price_unit'] = line.price_unit
                price.append(list_obj['quantity'])
                uom.append(list_obj['uom'])
                line_list.append(list_obj)

        pi_list = []
        if shipment_obj.lc_id.pi_ids_temp:
            for pi in shipment_obj.lc_id.pi_ids_temp:
                pi_obj = {}
                pi_obj['number'] = pi.name
                pi_obj['date'] = pi.invoice_date
                pi_list.append(pi_obj)

        price_total = sum(price)
        total = shipment_obj.invoice_value
        amt_to_word = self.env['res.currency'].amount_to_word(float(total), False)
        docargs = {
            'data': data,
            'lists': line_list,
            'price_total': price_total,
            'amt_to_word': amt_to_word,
            'pi_list': pi_list,
            'uom': uom[0],

        }
        return self.env['report'].render('lc_sales_product.report_bill_exchange_second', docargs)