from odoo import api, models
from odoo.tools.misc import formatLang


class PurchaseSummaryReport(models.AbstractModel):
    _name = 'report.purchase_reports.purchase_summary_template'
    sql_str = """ """

    @api.multi
    def render_html(self, docids, data=None):

        report_title = ''

        record_list = []
        data['operating_unit'] = ', '.join(data['operating_unit_name'])
        data['ou'] = data['operating_unit_name']
        data['pur_month'] = ', '.join(data['purchase_month'])
        data['pur_year'] = data['pur_year']

        if data['report_type'] == 'local':

            report_title = 'Purchase Summary(Local)'

        else:
            report_title = 'Purchase Summary(Foreign)'


        list_obj = {}
        list_obj['ou'] = data['ou']
        list_obj['month'] = data['purchase_month']
        list_obj['value'] = ['25000','3600','25896','87965',]
        list_obj['remarks'] = 'This is a Lab Product'
        list_obj['department'] = 'Production'
        record_list.append(list_obj)

        docargs = {
            'data': data,
            'report_title': report_title,
            'lists': record_list,

        }

        return self.env['report'].render('purchase_reports.purchase_summary_template', docargs)
