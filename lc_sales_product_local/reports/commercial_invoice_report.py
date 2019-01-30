from odoo import api, fields, models, _
from odoo.tools.misc import formatLang



class CommercialInvoice(models.AbstractModel):
    _name = 'report.lc_sales_product_local.report_commercial_invoice'

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

        data['company_id'] = shipment_obj.company_id.name
        data['factory'] = report_utility_pool.getAddressByUnit(shipment_obj.operating_unit_id)
        data['buyer'] = shipment_obj.lc_id.second_party_applicant.name
        data['buyer_address'] = report_utility_pool.getCoustomerAddress(shipment_obj.lc_id.second_party_applicant)
        data['invoice_id'] = "" if shipment_obj.invoice_id.id == False else shipment_obj.invoice_id.display_name
        data['invoice_date'] = "" if shipment_obj.invoice_id.id == False else report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(shipment_obj.invoice_id.date_invoice))
        data['terms_condition'] = shipment_obj.lc_id.terms_condition
        data['lc_id'] = shipment_obj.lc_id.unrevisioned_name
        data['lc_date'] = report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(shipment_obj.lc_id.issue_date))
        data['second_party_bank'] = shipment_obj.lc_id.second_party_bank
        data['currency_id'] = shipment_obj.lc_id.currency_id.name

        for pi_id in shipment_obj.lc_id.pi_ids:
            pi_id_list.append({'pi_id':pi_id.name,'pi_date':report_utility_pool.getERPDateFormat(report_utility_pool.getDateTimeFromStr(pi_id.create_date))})


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

        return self.env['report'].render('lc_sales_product_local.report_commercial_invoice', docargs)
