from odoo import api, models, fields, _
from odoo import exceptions

class AttendanceSummaryReport(models.AbstractModel):
    _name = "report.gbs_hr_attendance_report.report_att_summ_temp"

    @api.model
    def render_html(self, docids, data=None):
        if len(data['department_id'])==1:
            dept = self.env['hr.department'].search([('id', '=', data['department_id'][0])])
        else:
            dept = self.env['hr.department'].search([('id', 'in', data['department_id'])])
        dpt_att_summary_list = []
        sn = 1
        emp_data_list = self.get_data(data)
        if emp_data_list is not False:
            for d in dept:
                dpt_att_summary = {}
                # dept_id = d.id
                dpt_att_summary['name'] = d.name
                dpt_att_summary['seq'] = d.sequence
                dpt_att_summary['val'] = []

                for emp_data in emp_data_list:
                    if d.id == emp_data['dept']:
                        dpt_att_summary['val'].append(emp_data)
                for ps in dpt_att_summary['val']:
                    ps['sn'] = sn
                    sn += 1
                emp_sort_list = dpt_att_summary['val']
                emp_sort_list = sorted(emp_sort_list, key=lambda k: k['sn'])
                dpt_att_summary['val'] = emp_sort_list
                dpt_att_summary_list.append(dpt_att_summary)
        docargs = {
            'docs': dpt_att_summary_list,
            'data': data,
            'company': data['company_name'],
            'operating_unit': data['ou_name'],
            'docs_len': 20
        }
        return self.env['report'].render('gbs_hr_attendance_report.report_att_summ_temp', docargs)

    def get_data(self, data):

        emp_objs = self.env['hr.employee'].search([('company_id', '=', data['company_id']),
                                                   ('operating_unit_id', 'in', data['operating_unit_id']),
                                                   ('department_id', 'in', data['department_id'])])

        filtered_emp_list = emp_objs.filtered(
            lambda x: len(set(data['emp_tag_ids']).intersection(set(x.category_ids.ids))) > 0 or not x.category_ids.ids)

        if filtered_emp_list:
            report_data = []
            for record in filtered_emp_list:
                report_summary = {}
                report_summary['emp_name'] = record.name
                report_summary['designation'] = record.job_id.name
                report_summary['emp_seq'] = record.employee_sequence
                report_summary['dept'] = record.department_id.id
                absent_data_obj = self.env['hr.attendance.absent.day'].search([('date', '>=', data['date_from']),
                                                                               ('date', '<=', data['date_to'])])
                filtered_absent_data_obj = absent_data_obj.filtered(
                    lambda x: x.att_summary_line_id.employee_id.id == record.id and x.att_summary_line_id.state == 'approved')
                report_summary['absent_days'] = len(filtered_absent_data_obj)

                late_data_obj = self.env['hr.attendance.late.day'].search([('date', '>=', data['date_from']),
                                                                               ('date', '<=', data['date_to'])])
                filtered_late_data_obj = late_data_obj.filtered(
                    lambda x: x.att_summary_line_id.employee_id.id == record.id and x.att_summary_line_id.state == 'approved')
                report_summary['late_days'] = len(filtered_late_data_obj)

                report_data.append(report_summary)

            return report_data

        else:
            return False








