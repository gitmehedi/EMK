from odoo import api,models,fields
from odoo.tools.misc import formatLang


class PurchaseReport(models.AbstractModel):
    _name = "report.purchase_reports.report_purchase_material_requisition"

    sql_str = """ """

    @api.multi
    def render_html(self,docids,data=None):

        report_title = ''

        record_list = []
        data['operating_unit_id'] = data['operating_unit_id']
        data['dept_location_id'] = data['dept_location_id']
        data['date_from'] = data['date_from']
        data['date_to'] = data['date_to']

        if data['report_type'] == 'local':

            report_title = 'Purchase Material Requisition(Local)'

        else:
            report_title = 'Purchase Material Requisition(Foreign)'

        # self._cr.execute(self.sql_str)
        # data_list = self._cr.fetchall()

        #for row in data_list:
        list_obj = {}
        list_obj['ref'] = 'MRR NO-4648'
        list_obj['particulars'] = '39.033.002-Air Condition Splite Type-02(220 V,2400 BTU): For Lab'
        list_obj['qty'] = '10,000'
        list_obj['unit'] = 'Pair'
        list_obj['rate'] = formatLang(self.env, 66000)
        list_obj['discount'] = '5'
        list_obj['amount'] = formatLang(self.env, 66000)
        list_obj['remarks'] = 'This is a Lab Product'
        record_list.append(list_obj)

        docargs = {
            'data': data,
            'report_title':report_title,
            'lists': record_list,

        }
        return self.env['report'].render('purchase_reports.report_purchase_material_requisition', docargs)