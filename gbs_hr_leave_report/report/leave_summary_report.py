# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrHolidaySummaryReport(models.AbstractModel):
    _name = 'report.gbs_hr_leave_report.report_emp_leave_summary'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('gbs_hr_leave_report.report_emp_leave_summary')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': data['ids'],
            'form': data['form'],
            'other': data['other']
        }
        return report_obj.render('gbs_hr_leave_report.report_emp_leave_summary', docargs)

    # @api.model
    # def render_html(self, data=None):
    #     Report = self.env['report']
    #     holidays_report = Report._get_report_from_name('gbs_hr_leave_report.report_emp_leave_summary')
    #     holidays = self.env['hr.holidays'].browse(self.ids)
    #     docargs = {
    #         'doc_ids': self.ids,
    #         'doc_model': holidays_report.model,
    #         'docs': holidays,
    #         'get_header_info': self._get_header_info(data['form']['form_date'], data['form']['to_date']),
    #         'get_data_from_report': self._get_data_from_report(data['form']),
    #         'get_holidays_status': self._get_holidays_status(),
    #     }
    #     return Report.render('gbs_hr_leave_report.report_emp_leave_summary', docargs)