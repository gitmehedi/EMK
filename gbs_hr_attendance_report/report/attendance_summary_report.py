from odoo import api, models, fields, _
import datetime

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

        if len(data['emp_tag_ids']) > 0:
            emp_objs = emp_objs.filtered(
                lambda x: len(set(data['emp_tag_ids']).intersection(set(x.category_ids.ids))) > 0)

        if emp_objs:
            report_data = []
            for record in emp_objs:
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

                ot_data_obj = self.env['hr.ot.requisition'].search([('state', '=', 'approved'),
                                                                    ('employee_id', '=', record.id),
                                                                    ('from_datetime', '>=', data['date_from']),
                                                                    ('from_datetime', '<=', data['date_to']),
                                                                    ('to_datetime', '>=', data['date_from']),
                                                                    ('to_datetime', '<=', data['date_to'])])
                ot_data = '00:00'
                if ot_data_obj:
                    ot_data = self._get_total_ot_hours(ot_data_obj)
                report_summary['ot_hours'] = ot_data if ot_data else 0.0

                report_data.append(report_summary)

            return report_data

        else:
            return False

    def _get_total_ot_hours(self, ot_data_obj):
        seconds = 0
        for obj in ot_data_obj:
            start_dt = fields.Datetime.from_string(obj.from_datetime)
            finish_dt = fields.Datetime.from_string(obj.to_datetime)
            diff = finish_dt-start_dt
            seconds = seconds + float(diff.total_seconds())
        hours = float(seconds/3600)
        result = '{0:02.0f}:{1:02.0f}'.format(*divmod(hours * 60, 60))
        return result








