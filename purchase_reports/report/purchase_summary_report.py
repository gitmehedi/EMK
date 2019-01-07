from odoo import api, models
from odoo.tools.misc import formatLang


class PurchaseSummaryReport(models.AbstractModel):
    _name = 'report.purchase_reports.purchase_summary_template'
    sql_str = """ """

    @api.multi
    def render_html(self, docids, data=None):

        report_title = ''

        record_list = []
        data['operating_unit_id'] = data['operating_unit_id']
        data['pur_month'] = data['pur_month']

        if data['report_type'] == 'local':

            report_title = 'Purchase Summary(Local)'

        else:
            report_title = 'Purchase Summary(Foreign)'


        list_obj = {}
        list_obj['ou'] = ['SCCL-Dhaka','SCCL-CTG','SPPL-CTG']
        list_obj['month'] = ['January','February','March','April']
        list_obj['value'] = formatLang(self.env,['25000','3600','25896','87965',])
        list_obj['remarks'] = 'This is a Lab Product'
        list_obj['department'] = 'Production'
        record_list.append(list_obj)

        docargs = {
            'data': data,
            'report_title': report_title,
            'lists': record_list,

        }

        return self.env['report'].render('purchase_reports.purchase_summary_template', docargs)
