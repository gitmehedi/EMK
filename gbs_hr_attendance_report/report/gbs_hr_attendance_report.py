from openerp import api, fields, models
from datetime import date, datetime, timedelta




class GbsHrAttendanceDurationCalc(models.AbstractModel):
    _name = 'report.gbs_hr_attendance_report.report_individual_payslip2'
    
    @api.model
    def render_html(self, docids, data=None):
        check_in_out = data['check_in_out']
        type = data['type']
        department_id = data['department_id']
        employee_id = data['employee_id']
        from_date = data['from_date']
        to_date = data['to_date']

        attendance_pool = self.env['hr.attendance'].search([])

        dynamic_header = {}
        dynamic_header['emp_name'] = employee_id
        dynamic_header['department_name'] = department_id

        date_format = "%Y-%m-%d"
        start_date = datetime.strptime(from_date, date_format)
        end_date = datetime.strptime(to_date, date_format)
        delta = end_date - start_date

        dates_in_range_list = []
        day_month_list = []


        for i in range(delta.days + 1):
            dates_in_range = (start_date + timedelta(days=i))
            dates_in_range_list.append(dates_in_range)

        for dml in dates_in_range_list:
            day_month_dict = {}
            day_month_dict['day'] = dml.day
            day_month_dict['month'] = dml.month

            day_month_list.append(day_month_dict)

        docargs = {
            'docs': '',
            'dates_in_range': day_month_list,
        }

        return self.env['report'].render('gbs_hr_attendance_report.report_individual_payslip2', docargs)
