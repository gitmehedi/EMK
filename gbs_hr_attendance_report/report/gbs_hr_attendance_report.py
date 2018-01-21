from openerp import api, fields, models
from datetime import date, datetime
from datetime import timedelta

class GbsHeAttendanceReport(models.AbstractModel):
    _name = 'report.gbs_hr_attendance_report.report_attendance_doc'

    ###
    # Process Check In data
    ##
    def process_checkin_data_emp_dept_wise(self, str_date, employee_id):
        if(employee_id is not None):
            query = """SELECT 
                          MIN(check_in + interval '6h') 
                       FROM hr_attendance
                       WHERE employee_id = %s
                       AND date(check_in + interval '6h') = %s """
            self._cr.execute(query, tuple([employee_id, str_date]))
            result = self._cr.fetchall()

            if len(result) > 0:
                return result[0]
            else:
                return ''

    ##
    # Process Check Out data
    ##
    def process_checkout_data_emp_dept_wise(self, str_date, employee_id):
        if (employee_id is not None):
            query = """SELECT 
                          MAX(check_out + interval '6h') 
                       FROM hr_attendance
                       WHERE employee_id = %s
                       AND date(check_out + interval '6h') = %s"""
            self._cr.execute(query, tuple([employee_id, str_date]))
            result = self._cr.fetchall()

            if len(result) > 0:
                return result[0]
            else:
                return ''

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
        operating_unit_id = data['operating_unit_id']

        date_format = "%Y-%m-%d"
        start_date = datetime.strptime(from_date, date_format)
        end_date = datetime.strptime(to_date, date_format)
        delta = end_date - start_date

        dates_in_range_list = []
        all_val_list = []

        for i in range(delta.days + 1):
            dates_in_range = (start_date + timedelta(days=i))
            dates_in_range_list.append(dates_in_range)


        if(type == 'employee_type'):
            emp = self.env['hr.employee'].search([('id','=',employee_id)])
        elif (type == 'department_type'):
            emp = self.env['hr.employee'].search([('department_id', '=', department_id)])
        elif (type == 'op_type'):
            emp = self.env['hr.employee'].search([('operating_unit_id', '=', operating_unit_id)])

        dynamic_col_list = self.dynamic_col_list(dates_in_range_list, start_date, end_date)
        emp_sort_list = ''
        check_type_friendly_str = check_in_out

        for e in emp:
            res = {}
            res['emp_name'] = e.name_related
            res['designation'] = e.job_id.name
            res['dept'] = e.department_id.name
            res['emp_seq'] = e.employee_sequence

            for dyc in dynamic_col_list:
                if(check_in_out == 'check_in'):
                    result = str(self.process_checkin_data_emp_dept_wise(dyc, e.id))
                    self.datetime_manipulation(dyc, res, result)
                    check_type_friendly_str = 'Check In'

                elif(check_in_out == 'check_out'):
                    result = str(self.process_checkout_data_emp_dept_wise(dyc, e.id))
                    self.datetime_manipulation(dyc, res, result)
                    check_type_friendly_str = 'Check Out'

            all_val_list.append(res)
            emp_sort_list = all_val_list
            emp_sort_list = sorted(emp_sort_list, key=lambda k: k['emp_seq'])

        docargs = {
            'all_val_list': emp_sort_list,
            'dynamic_col_list': dynamic_col_list,
            'check_type_friendly_str': check_type_friendly_str,
        }

        return self.env['report'].render('gbs_hr_attendance_report.report_attendance_doc', docargs)

    def datetime_manipulation(self, dyc, res, result):
        if result == '':
            res[dyc] = result
        elif result == '(None,)':
            res[dyc] = ''
        else:
            result_datetime = result[13:21]
            res[dyc] = str(result_datetime)