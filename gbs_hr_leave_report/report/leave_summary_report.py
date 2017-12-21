# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrLeaveSummaryReport(models.AbstractModel):
    _name = 'report.gbs_hr_leave_report.report_emp_leave_summary'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        emp_pool = self.env['hr.employee']
        leave_pool = self.env['hr.holidays']
        if data['operating_unit_id']:
            operating_unit_id = data['operating_unit_id']
            from_date = data['from_date']
            to_date = data['to_date']
            holiday_objs = self.env['hr.holidays'].search([('employee_id.operating_unit_id', '=', operating_unit_id),
                                                           ('date_from', '>=', from_date),
                                                           ('date_to', '<=', to_date)])

            header = {}
            header[0] = 'SI'
            header[1] = 'Name'
            header[2] = 'Designation'
            header[3] = 'Department'
            header_data = self.env['hr.holidays.status'].search([])
            for val in header_data:
                header[len(header)] = {val.name: {'Avail': 0, 'Balance': 0}}

        docargs = {
            'form_date': data['from_date'],
            'to_date': data['to_date'],
            'holiday_objs': holiday_objs,
            'operating_unit': data['operating_unit_id'],
            'header': header
        }
        return report_obj.render('gbs_hr_leave_report.report_emp_leave_summary', docargs)
