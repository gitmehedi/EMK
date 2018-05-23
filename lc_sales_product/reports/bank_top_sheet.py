from odoo import api, fields, models, _

class BankTopSheet(models.AbstractModel):
    _name = 'report.lc_sales_product.report_top_sheet'

    @api.multi
    def render_html(self, docids, data=None):
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.browse(data.get('shipment_id'))
        report_utility_pool = self.env['report.utility']
        doc_list = []
        data = {}
        data['first_party_bank'] = report_utility_pool.getBankAddress(shipment_obj.lc_id.first_party_bank)
        data['company'] = shipment_obj.company_id.name
        if shipment_obj.lc_id.lc_document_line:
            for line in shipment_obj.lc_id.lc_document_line:
                doc_obj = {}
                doc_obj['name'] = line.doc_name
                doc_obj['original'] = line.original
                doc_obj['copy'] = line.copy
                doc_list.append(doc_obj)

        docargs = {
            'data': data,
            'lists': doc_list,

        }
        return self.env['report'].render('lc_sales_product.report_top_sheet', docargs)