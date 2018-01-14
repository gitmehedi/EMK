from odoo import api, fields, models, _
import datetime
from datetime import timedelta


class HrAttendanceErrorSummaryReport(models.AbstractModel):
    _name = 'report.gbs_hr_attendance_report.report_att_error_summary'

    @api.multi
    def render_html(self, docids, data=None):

        attendance_pool = self.env['hr.attendance']
        docs = attendance_pool.search([],limit = 1)

        data_list = []
        # requested_date = data['required_date']
        # curr_time_gmt = datetime.datetime.now()
        # current_time = curr_time_gmt + timedelta(hours=6)
        dept_pool = self.env['hr.department'].search([])

        if data['type'] == "unit_type":

            for dept in dept_pool:
                dpt_list = {}
                dpt_list['name'] = dept.name
                dpt_list['seq'] = dept.sequence
                dpt_list['val'] = []

                for doc in docs:
                    emp_list = {}
                    emp_list['name'] = doc.employee_id.name_related
                    emp_list['acc_no'] = doc.employee_id.device_employee_acc
                    emp_list['designation'] = doc.employee_id.job_id.name
                    emp_list['check_in'] = doc.check_in
                    emp_list['check_out'] = doc.check_out

                    dpt_list['val'].append(emp_list)

                data_list.append(dpt_list)

        elif data['type'] == "department_type":
            print type
        elif data['type'] == "employee_type":
            print type


        docargs = {
            'data': data,
            'data_list': data_list,
            'data_list_len': 6,
        }

        return self.env['report'].render('gbs_hr_attendance_report.report_att_error_summary', docargs)