from odoo import api, fields, models, _
import datetime
from datetime import timedelta
from openerp.addons.gbs_hr_attendance_utility.models.utility_class import Employee


class HrAttendanceErrorSummaryReport(models.AbstractModel):
    _name = 'report.gbs_hr_attendance_report.attendance_error_summary_report'

    @api.multi
    def render_html(self, docids, data=None):

        report_obj = self.env['report']

        requested_date = data['required_date']
        curr_time_gmt = datetime.datetime.now()
        current_time = curr_time_gmt + timedelta(hours=6)

        if data['type'] == "unit_type":
            print type
        elif data['type'] == "department_type":
            print type
        elif data['type'] == "department_type":
            print type

        # data['operating_unit_id'] = self.operating_unit_id.id
        # data['department_id'] = self.emp_id.department_id.id
        # data['emp_id'] = self.emp_id.id
        # data['from_date'] = self.from_date
        # data['to_date'] = self.to_date

        docargs = {
            'required_date': data['required_date'],
            'created_on': curr_time_gmt,
            'company_name': companyName,
            'att_summary_list': att_summary_list,
            'operating_unit': data['operating_unit_id']
        }

        docargs = {
            'data': data,
            'holiday_objs': lists,
            'header': header
        }

        return self.env['report'].render('gbs_hr_attendance_report.attendance_error_summary_report', docargs)