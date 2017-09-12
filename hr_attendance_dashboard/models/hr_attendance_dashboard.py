import json
import datetime
from odoo import api, fields, models,tools
from datetime import date,timedelta
from openerp.addons.gbs_hr_attendance_utility.models.utility_class import Employee
from openerp.addons.gbs_hr_attendance_report.report.hr_daily_attendance_report import GetDailyAttendanceReport


class HrAttendanceDashboard(models.Model):
    _inherit = "operating.unit"


    @api.one
    def _kanban_dashboard(self):
        self.kanban_dashboard = json.dumps(self.get_journal_dashboard_datas())

    kanban_dashboard = fields.Text(compute='_kanban_dashboard')

    @api.multi
    def get_journal_dashboard_datas(self):
        emp_pool = self.env['hr.employee']
        att_utility_pool = self.env['attendance.utility']
        op_pool = self.env['operating.unit']

        requested_date = date.today().strftime('%Y-%m-%d')
        curr_time_gmt = datetime.datetime.now()
        current_time = curr_time_gmt + timedelta(hours=6)
        graceTime = att_utility_pool.getGraceTime(requested_date)


        unit = op_pool.search([('id', '=', self.id)])

        att_summary = self.getSummaryByUnit(unit,requested_date, graceTime, emp_pool, att_utility_pool, current_time)

        return {
            'total_emp':att_summary["total_emp"],
            'on_time_present':len(att_summary["on_time_present"]),
            'late':len(att_summary["late"]),
            'absent':len(att_summary["absent"])
        }


    def getSummaryByUnit(self, unit,requested_date, graceTime,  emp_pool, att_utility_pool, current_time):

        operating_unit_id = unit.id

        day = datetime.timedelta(days=1)

        requestedDate = att_utility_pool.getDateFromStr(requested_date)

        att_summary = {"unit_name": unit.name, "total_emp": 0, "on_time_present": [],"late": [], "absent": [], "leave": [],
                       "short_leave": [], "rest": [],"roster_obligation": [], "unworkable": [],
                       "holidays": [], "alter_roster": []}

        employeeList = emp_pool.search([('operating_unit_id', '=', operating_unit_id),
                                        ('active', '=', True), ('is_monitor_attendance', '=', True)
                                        ], order='department_id,employee_sequence desc')

        employeeAttMap = att_utility_pool.getDailyAttByDateAndUnit(requestedDate, operating_unit_id)

        att_summary["total_emp"] = len(employeeList)

        for employee in employeeList:

            employeeId = employee.id

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
                    att_summary = att_utility_pool.makeDecisionForADays(att_summary, employeeAttMap, requested_date, currentDaydutyTime, employee, graceTime)
                else:
                    att_summary["unworkable"].append(Employee(employee))

        return att_summary

