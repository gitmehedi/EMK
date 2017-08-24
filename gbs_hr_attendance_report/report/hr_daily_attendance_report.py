from odoo import api, fields, models
import datetime
from datetime import timedelta
from openerp.addons.gbs_hr_attendance_utility.models.utility_class import Employee

class GetDailyAttendanceReport(models.AbstractModel):
    _name='report.gbs_hr_attendance_report.report_daily_att_doc'

    @api.model
    def render_html(self, docids, data=None):

        emp_pool = self.env['hr.employee']
        att_utility_pool = self.env['attendance.utility']

        att_summary_list = []

        # Get exclude employee acc number
        exclude_emp_pool = self.env['hr.excluded.employee'].search([])
        exclude_emp_res = []
        for i in exclude_emp_pool:
            exclude_emp_res.append(i.acc_number)

        requested_date = data['required_date']
        current_time =  datetime.datetime.now()
        graceTime = att_utility_pool.getGraceTime(requested_date)

        #@Todo- Getting operating unit by company and travers by unit
        operating_unit_id = data['operating_unit_id']
        att_summary = self.getSummaryByUnit(operating_unit_id, data, graceTime, exclude_emp_res, emp_pool, att_utility_pool, current_time)

        att_summary_list.append(att_summary)

        # if data['department_id']:
        #     employeeList = emp_pool.search([('operating_unit_id', '=', data['operating_unit_id']),
        #                                     ('department_id', '=', data['department_id']),
        #                                     ('active', '=', True), ('device_employee_acc', 'not in', exclude_emp_res)
        #                                     ], order='department_id,employee_sequence desc')
        #
        # else:
        #     employeeList = emp_pool.search([('operating_unit_id', '=', data['operating_unit_id']),
        #                                     ('active', '=', True), ('device_employee_acc', 'not in', exclude_emp_res)
        #                                     ], order='department_id,employee_sequence desc')


        docargs = {
            'required_date': data['required_date'],
            'required_on': data['required_date'],
            'required_by': data['required_date'],
            'att_summary_list': att_summary_list
        }

        return self.env['report'].render('gbs_hr_attendance_report.report_daily_att_doc', docargs)

    def getSummaryByUnit(self, operating_unit_id, data, graceTime, exclude_emp_res, emp_pool, att_utility_pool, current_time):

        requested_date = data['required_date']
        day = datetime.timedelta(days=1)
        requestedDate = att_utility_pool.getDateFromStr(requested_date)

        att_summary = {"total_emp": 0, "on_time_present": [],"late": [], "absent": [], "leave": [],
                       "short_leave": [], "rest": [],"roster_obligation": [], "unworkable": [],
                       "holidays": [], "alter_roster": []}

        employeeList = emp_pool.search([('operating_unit_id', '=', operating_unit_id),
                                        ('active', '=', True), ('device_employee_acc', 'not in', exclude_emp_res)
                                        ], order='department_id,employee_sequence desc')

        employeeAttMap = att_utility_pool.getDailyAttByDateAndUnit(requestedDate, operating_unit_id)

        att_summary["total_emp"] = len(employeeList)

        for employee in employeeList:

            employeeId = employee.id

            alterTimeMap = att_utility_pool.buildAlterDutyTime(requestedDate, requestedDate, employeeId)
            if alterTimeMap:
                att_summary["alter_roster"].append(Employee(employee))
                break

            dutyTimeMap = att_utility_pool.getDutyTimeByEmployeeId(employeeId, requestedDate, requestedDate)

            if len(dutyTimeMap) == 0:
                isSetRoster = att_utility_pool.isSetRosterByEmployeeId(employeeId, requestedDate, requestedDate)
                if isSetRoster == True:
                    att_summary["rest"].append(Employee(employee))
                else:
                    att_summary["roster_obligation"].append(Employee(employee))
                break
            else:
                currentDaydutyTime = dutyTimeMap.get(att_utility_pool.getStrFromDate(requestedDate))
                if currentDaydutyTime.startDutyTime < current_time:
                    att_summary = att_utility_pool.makeDecisionForADays(att_summary, employeeAttMap, requested_date, currentDaydutyTime, employee, graceTime)
                else:
                    att_summary["unworkable"].append(Employee(employee))

        return att_summary

        # if alterTimeMap.get(att_utility_pool.getStrFromDate(requested_date)):  # Check this date is alter date
        #     alterDayDutyTime = alterTimeMap.get(att_utility_pool.getStrFromDate(requested_date))
        #     attendanceDayList = att_utility_pool.getAttendanceListByAlterDay(alterDayDutyTime, day, dutyTimeMap,
        #                                                                      employeeId)
        #
        #     att_summary = att_utility_pool.makeDecisionForADays(att_summary, attendanceDayList, requested_date,
        #                                                         alterDayDutyTime, employee)
        #
        # elif dutyTimeMap.get(att_utility_pool.getStrFromDate(requested_date)):
        #     currentDaydutyTime = dutyTimeMap.get(att_utility_pool.getStrFromDate(requested_date))
        #     att_summary = att_utility_pool.makeDecisionForADays(att_summary, attendanceDayList, requested_date,

    @api.model
    def render_html_5(self, docids, data=None):
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