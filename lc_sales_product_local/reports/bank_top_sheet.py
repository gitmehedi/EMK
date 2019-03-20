from odoo import api, fields, models, _
from odoo.tools.misc import formatLang

class BankTopSheet(models.AbstractModel):
    _name = 'report.lc_sales_product_local.report_top_sheet'

    @api.multi
    def render_html(self, docids, data=None):
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.browse(data.get('shipment_id'))
        report_utility_pool = self.env['report.utility']
        doc_list = []
        data = {}
        data['first_party_branch_bank'] = shipment_obj.lc_id.first_party_bank_acc.bank_id.name
        data['first_party_branch_add'] = report_utility_pool.getBranchAddress2(shipment_obj.lc_id.first_party_bank_acc)
        data['company'] = shipment_obj.company_id.name
        data['currency_id'] = shipment_obj.lc_id.currency_id.name
        data['invoice_value'] = formatLang(self.env,shipment_obj.invoice_value)
        data['lc_id'] = shipment_obj.lc_id.unrevisioned_name
        data['issue_date'] = report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(shipment_obj.lc_id.issue_date))
        if shipment_obj.lc_id.lc_document_line:
            for line in shipment_obj.lc_id.lc_document_line:
                doc_obj = {}
                doc_obj['name'] = line.doc_name.name
                doc_obj['original'] = line.original
                doc_obj['copy'] = line.copy
                doc_list.append(doc_obj)

        docargs = {
            'data': data,
            'lists': doc_list,

        }
        return self.env['report'].render('lc_sales_product_local.report_top_sheet', docargs)