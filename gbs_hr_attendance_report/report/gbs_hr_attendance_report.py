from openerp import api, fields, models
from datetime import date, datetime
from datetime import timedelta

class GbsHrAttendanceDurationCalc(models.AbstractModel):
    _name = 'report.gbs_hr_attendance_report.report_individual_payslip2'

    def process_checkin_data_empwise(self, str_date, employee_id):
        if(employee_id is not None):
            query = """SELECT min(check_in) FROM hr_attendance
                                         WHERE employee_id=%s
                                         AND check_in > %s
                                         GROUP BY employee_id"""
            self._cr.execute(query, tuple([employee_id, str_date]))
            result = self._cr.fetchall()
            if len(result) > 0:
                return result[0]
            else:
                return ''

    def process_checkin_data_deptwise(self, min_check_in, max_checkin, department_id):
        if(department_id is not None):
            query = """SELECT min(check_in) FROM hr_attendance
                                                     WHERE department_id=%s
                                                     AND check_in > %s
                                                     GROUP BY department_id"""

            self._cr.execute(query, tuple([department_id, min_check_in]))

        return self._cr.fetchall()

    def dynamic_col_list(self, dyc, from_date, to_date):

        dynamic_col = []
        while(from_date <= to_date):

            str_date = str(from_date)
            key = str_date[:10]
            dynamic_col.append(key)
            from_date += timedelta(days=1)

        return dynamic_col



    @api.model
    def render_html(self, docids, data=None):
        check_in_out = data['check_in_out']
        type = data['type']
        department_id = data['department_id']
        employee_id = data['employee_id']
        from_date = data['from_date']
        to_date = data['to_date']

        date_format = "%Y-%m-%d"
        start_date = datetime.strptime(from_date, date_format)
        end_date = datetime.strptime(to_date, date_format)
        delta = end_date - start_date

        dates_in_range_list = []
        all_val_list = []

        min_checkin = datetime.combine(start_date, datetime.min.time())
        max_checkin = datetime.combine(start_date, datetime.max.time())

        for i in range(delta.days + 1):
            dates_in_range = (start_date + timedelta(days=i))
            dates_in_range_list.append(dates_in_range)


        if(type == 'employee_type'):
            emp = self.env['hr.employee'].search([('id','=',employee_id)])
        elif (type == 'department_type'):
            emp = self.env['hr.employee'].search([('department_id', '=', department_id)])

        dynamic_col_list = self.dynamic_col_list(dates_in_range_list, start_date, end_date)
        for e in emp:
            res = {}
            res['emp_name'] = e.name_related
            res['designation'] = e.job_id.name
            res['dept'] = e.department_id.name

            for dyc in dynamic_col_list:
                result = str(self.process_checkin_data_empwise(dyc, e.id))
                res[dyc] = result[13:18]


            # if (check_in_out == 'check_in'):
            #     if (type == 'employee_type'):
            #         check_in_data = self.process_checkin_data_empwise(min_checkin, max_checkin, employee_id)
            #     # if (type == 'department_type'):
            #     #     check_in_data = self.process_checkin_data_deptwise(min_checkin, max_checkin, department_id)
            #
            #     res['check_in_data'] = check_in_data

            all_val_list.append(res)

        docargs = {
            'all_val_list': all_val_list,
            #'dyc_list': dyc_list,
        }

        return self.env['report'].render('gbs_hr_attendance_report.report_individual_payslip2', docargs)
