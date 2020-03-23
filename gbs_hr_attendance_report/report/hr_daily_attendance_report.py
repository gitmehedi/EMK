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
        op_pool = self.env['operating.unit']

        att_summary_list = []


        requested_date = data['required_date']

        # short lave count
        # from_date = str(str(data['required_date']) + ' 00:00:00')
        # to_date = str(str(data['required_date']) + ' 23:59:59')
        from_date_str = str(str(data['required_date']) + ' 00:00:00')
        to_date_str = str(str(data['required_date']) + ' 23:59:59')
        from_date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d %H:%M:%S') - timedelta(hours=6)
        to_date = datetime.datetime.strptime(to_date_str, '%Y-%m-%d %H:%M:%S') - timedelta(hours=6)
        short_leave_obj = self.env['hr.short.leave'].search([('date_from', '>=', str(from_date)),
                                                             ('date_to', '<=', str(to_date)),
                                                             ('state', '=', 'validate')])

        curr_time_gmt = datetime.datetime.now()
        current_time = curr_time_gmt + timedelta(hours=6)
        graceTime = att_utility_pool.getGraceTime(requested_date)

        companyName = ""

        if data['operating_unit_id']:
            operating_unit_id = data['operating_unit_id']
            unit = op_pool.search([('id','=',operating_unit_id)])
            companyName = unit.company_id.name
            # short leave count
            filtered_short_leave_obj = short_leave_obj.filtered(lambda x: x.employee_id.operating_unit_id.id == operating_unit_id)
            short_leave_count = len(filtered_short_leave_obj)

            att_summary = self.getSummaryByUnit(unit, data, graceTime,  emp_pool, att_utility_pool, current_time)
            att_summary_list.append(att_summary)
        else:

            unitList = op_pool.search([('company_id','=',data['company_id'])])
            if unitList:
                companyName = unitList[0].company_id.name

            for unit in unitList:
                att_summary = self.getSummaryByUnit(unit, data, graceTime, emp_pool,
                                                att_utility_pool, current_time)
                att_summary_list.append(att_summary)

        docargs = {
            'required_date': data['required_date'],
            'created_on': curr_time_gmt,
            'company_name': companyName,
            'att_summary_list': att_summary_list,
            'operating_unit':data['operating_unit_id'],
            'short_leave_count': short_leave_count
        }

        return self.env['report'].render('gbs_hr_attendance_report.report_daily_att_doc', docargs)

    def getSummaryByUnit(self, unit, data, graceTime,  emp_pool, att_utility_pool, current_time):

        operating_unit_id = unit.id

        requested_date = data['required_date']
        day = datetime.timedelta(days=1)
        requestedDate = att_utility_pool.getDateFromStr(requested_date)

        att_summary = {"unit_name": unit.name, "total_emp": 0, "on_time_present": [],"late": [], "absent": [], "leave": [],
                       "short_leave": [], "rest": [],"roster_obligation": [], "unworkable": [],
                       "holidays": [], "alter_roster": []}

        employeeList = emp_pool.search([('operating_unit_id', '=', operating_unit_id),
                                        ('active', '=', True)],
                                       order='department_id,employee_sequence desc')

        employeeAttMap = att_utility_pool.getDailyAttByDateAndUnit(requestedDate, operating_unit_id)

        # Getting data for holidays

        compensatoryLeaveMap = {}
        oTMap = {}
        todayIsHoliday = False
        holidayMap = att_utility_pool.getHolidaysByUnit(operating_unit_id, requested_date)
        if holidayMap.get(requested_date):
            lineId = holidayMap.get(requested_date)
            todayIsHoliday = True
            compensatoryLeaveMap = att_utility_pool.getCompensatoryLeaveEmpByHolidayLineId(lineId)
            oTMap = att_utility_pool.getOTEmpByHolidayLineId(lineId)

        # End Getting data for holidays

        att_summary["total_emp"] = len(employeeList)

        for employee in employeeList:

            employeeId = employee.id

            if employee.is_monitor_attendance == False:
                if todayIsHoliday == True:
                    att_summary["holidays"].append(Employee(employee))
                else:
                    att_summary["on_time_present"].append(Employee(employee))
                continue

            alterTimeMap = att_utility_pool.buildAlterDutyTime(requestedDate, requestedDate, employeeId)
            if alterTimeMap:
                att_summary["alter_roster"].append(Employee(employee))
                continue

            dutyTimeMap = att_utility_pool.getDutyTimeByEmployeeId(employeeId, requestedDate, requestedDate)

            if len(dutyTimeMap) == 0:
                isSetRoster = att_utility_pool.isSetRosterByEmployeeId(employeeId, requestedDate, requestedDate)
                if isSetRoster == True:
                    att_summary["rest"].append(Employee(employee))
                else:
                    att_summary["roster_obligation"].append(Employee(employee))
                    continue
            else:
                currentDaydutyTime = dutyTimeMap.get(att_utility_pool.getStrFromDate(requestedDate))
                if currentDaydutyTime.startDutyTime < current_time:
                    att_summary = att_utility_pool.makeDecisionForADays(att_summary, employeeAttMap, requested_date,
                                                                        currentDaydutyTime, employee, graceTime,
                                                                        todayIsHoliday, compensatoryLeaveMap, oTMap)
                else:
                    att_summary["unworkable"].append(Employee(employee))

        return att_summary
