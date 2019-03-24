from odoo import api, fields, models, _
from odoo.tools.misc import formatLang

class BankTopSheet(models.AbstractModel):
    _name = 'report.lc_sales_product_local.report_party_receiving'

    @api.multi
    def render_html(self, docids, data=None):
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.browse(data.get('shipment_id'))
        report_utility_pool = self.env['report.utility']
        doc_list = []
        pi_id_list = []
        data = {}
        data['buyer'] = shipment_obj.lc_id.second_party_applicant.name
        data['buyer_address'] = report_utility_pool.getCoustomerAddress(shipment_obj.lc_id.second_party_applicant)
        for pi_id in shipment_obj.lc_id.pi_ids:
            pi_id_list.append({'pi_id':pi_id.name,'pi_date':report_utility_pool.getERPDateFormat(report_utility_pool.getDateTimeFromStr(pi_id.create_date))})

        data['lc_id'] = shipment_obj.lc_id.unrevisioned_name
        data['lc_date'] = report_utility_pool.getERPDateFormat(
            report_utility_pool.getDateFromStr(shipment_obj.lc_id.issue_date))
        data['company'] = shipment_obj.company_id.name
        data['invoice_date'] = "" if shipment_obj.invoice_id.id == False else report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(shipment_obj.invoice_id.date_invoice))
        data['currency_id'] = shipment_obj.lc_id.currency_id.name
        data['invoice_value'] = formatLang(self.env,shipment_obj.invoice_value)
        data['issue_date'] = report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(shipment_obj.lc_id.issue_date))

        docargs = {
            'data': data,
            'pi_id_list': pi_id_list,
            'lists': doc_list,

        }
        return self.env['report'].render('lc_sales_product_local.report_party_receiving', docargs)