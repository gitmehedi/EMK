from odoo import api, fields, models
from datetime import datetime


class GetDailyAttendanceReport(models.AbstractModel):
    _name='report.gbs_hr_attendance_report.report_daily_att_doc'

    @api.model
    def render_html(self, docids, data=None):
        emp_pool=self.env['hr.employee']

        if data['department_id']:
            emp_dept_ids = emp_pool.search([('operating_unit_id', '=', data['operating_unit_id']),
                                       ('department_id', '=', data['department_id'])
                                       ])
            res_emp_ids = emp_dept_ids.ids
        else:
            emp_ids=emp_pool.search([('operating_unit_id', '=', data['operating_unit_id'])])
            res_emp_ids = emp_ids.ids

        required_date = data['required_date']
        str_end_dt = data['required_date'] + ' 23:59:59'
        # from time schedule start
        # from time schedule end
        # data['required_date'] + ' 03:15:00'
        str_in_time_dt = data['required_date'] + ' 03:15:00'

        start_datetime = datetime.strptime(required_date,"%Y-%m-%d")
        end_datetime = datetime.strptime(str_end_dt,"%Y-%m-%d %H:%M:%S")

        result_total_present=[]
        result_total_late=[]
        result_late_list=[]
        result_absent_list=[]

        if res_emp_ids:
            query = """select distinct employee_id from hr_attendance
                        where employee_id in %s
                        and check_in between %s
                        and %s
                        group by employee_id"""
            self._cr.execute(query, tuple([tuple(res_emp_ids), start_datetime, end_datetime]))
            result_total_present = self._cr.fetchall()

            if result_total_present:
                for emp_tpl in result_total_present:
                    query = """select distinct TO_CHAR((((hour_from+grace_time)-6) || ' hour')::interval, 'HH24:MI:SS') as check_in
                               from hr_employee e join hr_shifting_history s on s.employee_id=e.id
                               join resource_calendar_attendance r on r.calendar_id=s.shift_id 
                               where %s between effective_from and effective_end and e.id=%s"""
                    self._cr.execute(query, tuple([required_date,emp_tpl[0]]))
                    str_in_grace_time = self._cr.fetchone()
                    if str_in_grace_time:
                        str_in_time_dt=data['required_date'] + ' '+str_in_grace_time[0]


                    query1 = """select * from (select employee_id, min(check_in) as check_in from hr_attendance
                                where employee_id =%s
                                and check_in between %s
                                and  %s
                                group by employee_id) as t
                                where check_in > %s
                              """
                    self._cr.execute(query1, tuple([emp_tpl[0], start_datetime, end_datetime, str_in_time_dt]))
                    result_late = self._cr.fetchone()
                    if result_late:
                        result_total_late.append(result_late[0])

                    query2 = """select e.name_related as emp_name, 
                                d.name as emp_dept, j.name as emp_desi,to_char((min(t.check_in)+interval '6hr')::timestamp with time zone, 'HH24:MI:SS'::text) AS check_in  
                                from hr_employee e
                                left join hr_department d on d.id = e.department_id
                                left join hr_job j on j.id = e.job_id
                                join hr_attendance t on t.employee_id = e.id
                                where e.id in (select employee_id from (
                                select employee_id, min(check_in) as check_in from hr_attendance
                                where employee_id = %s
                                and check_in between %s
                                and  %s 
                                group by employee_id) as t where check_in > %s)and check_in between %s
                                and  %s  group by e.name_related,d.name,j.name"""
                    self._cr.execute(query2, tuple([emp_tpl[0], start_datetime, end_datetime, str_in_time_dt, start_datetime,end_datetime]))
                    late_list = self._cr.fetchone()
                    if late_list:
                        result_late_list.append(late_list)


            query = """select e.name_related as emp_name, 
                        d.name as emp_dept, j.name as emp_desi from hr_employee e
                        left join hr_department d on d.id = e.department_id
                        left join hr_job j on j.id = e.job_id
                        where e.id in %s
                        and e.id not in 
                        (select employee_id from hr_attendance
                        where employee_id in %s
                        and check_in between %s
                        and  %s
                        group by employee_id)"""
            self._cr.execute(query, tuple([tuple(res_emp_ids),tuple(res_emp_ids), start_datetime, end_datetime]))
            result_absent_list = self._cr.fetchall()

        data_total_present_employee = len(result_total_present)
        data_total_absent_employee = len(res_emp_ids) - len(result_total_present)
        data_total_late_employee = len(result_total_late)

        data_absent_list = result_absent_list
        data_late_list =result_late_list

        docargs = {
            'required_date': data['required_date'],
            'total_present_employee':data_total_present_employee,
            'total_absent_employee':data_total_absent_employee,
            'total_late_employee':data_total_late_employee,
            'absent_list':data_absent_list,
            'late_list':data_late_list
        }

        return self.env['report'].render('gbs_hr_attendance_report.report_daily_att_doc', docargs)