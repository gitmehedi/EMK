import json
import datetime
from odoo import api, fields, models,tools
from datetime import date,timedelta
from odoo.addons.gbs_hr_attendance_utility.models.utility_class import Employee


class HrAttendanceDashboard(models.Model):
    _inherit = "hr.department"


    @api.one
    def _kanban_dashboard(self):
        self.kanban_dashboard = json.dumps(self.get_attendance_dashboard_datas())

    kanban_dashboard = fields.Text(compute='_kanban_dashboard')
    kanban_dashboard_graph = fields.Text(compute='_kanban_dashboard')
    color = fields.Integer(string='Color Index', help="The color of the team")

    @api.multi
    def get_attendance_dashboard_datas(self):
        emp_pool = self.env['hr.employee']
        att_utility_pool = self.env['attendance.utility']
        # op_pool = self.env['operating.unit']


        requested_date = date.today().strftime('%Y-%m-%d')
        curr_time_gmt = datetime.datetime.now()
        current_time = curr_time_gmt + timedelta(hours=6)
        graceTime = att_utility_pool.getGraceTime(requested_date)


        dept = self.search([('id', '=', self.id)])

        att_summary = self.getSummaryByDept(dept, requested_date, graceTime, emp_pool, att_utility_pool, current_time)

        return {
            'total_emp':att_summary["total_emp"],
            'on_time_present':len(att_summary["on_time_present"]),
            'late':len(att_summary["late"]),
            'absent':len(att_summary["absent"])
        }


    def getSummaryByDept(self, dept, requested_date, graceTime,  emp_pool, att_utility_pool, current_time):

        dept_id = dept.id

        requestedDate = att_utility_pool.getDateFromStr(requested_date)

        att_summary = {"dept_name": dept.name, "total_emp": 0, "on_time_present": [],"late": [], "absent": [], "leave": [],
                       "short_leave": [], "rest": [],"roster_obligation": [], "unworkable": [],
                       "holidays": [], "alter_roster": []}

        employeeList = emp_pool.search([('department_id', '=', dept_id),
                                        ('active', '=', True)],
                                       order='employee_sequence desc')


        employeeAttMap = att_utility_pool.getDailyAttByDateAndDept(requestedDate, dept_id)

        # Getting data for holidays

        compensatoryLeaveMap = {}
        oTMap = {}
        todayIsHoliday = False
        operating_unit_id = self.env['operating.unit'].search([('active','=', "TRUE")], limit=1).id
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

    @api.multi
    def dashboard_absent_employee_action_id(self):
        view = self.env.ref('hr_attendance_dashboard_dept.hr_att_absent_tree_view')

        emp_pool = self.env['hr.employee']
        att_utility_pool = self.env['attendance.utility']
        # op_pool = self.env['operating.unit']


        requested_date = date.today().strftime('%Y-%m-%d')
        curr_time_gmt = datetime.datetime.now()
        current_time = curr_time_gmt + timedelta(hours=6)
        graceTime = att_utility_pool.getGraceTime(requested_date)

        dept = self.search([('id', '=', self.id)])

        att_summary = self.getSummaryByDept(dept, requested_date, graceTime, emp_pool, att_utility_pool, current_time)

        res_ids=[]
        for i in att_summary["absent"]:
            res_ids.append(i.employeeId)
        # [i.employeeId for i in att_summary['absent']]
        if res_ids:
            return {
                'name': ('Absent Employee'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'hr.employee',
                'domain': [('id', '=', res_ids)],
                'view_id': [view.id],
                'context': {'create': False, 'edit': False},
                'type': 'ir.actions.act_window',
                'target':'new'
            }

    @api.multi
    def dashboard_late_employee_action_id(self):
        view = self.env.ref('hr_attendance_dashboard_dept.hr_att_late_tree_view')

        emp_pool = self.env['hr.employee']
        att_utility_pool = self.env['attendance.utility']
        # op_pool = self.env['operating.unit']

        requested_date = date.today().strftime('%Y-%m-%d')
        curr_time_gmt = datetime.datetime.now()
        current_time = curr_time_gmt + timedelta(hours=6)
        graceTime = att_utility_pool.getGraceTime(requested_date)

        dept = self.search([('id', '=', self.id)])

        att_summary = self.getSummaryByDept(dept, requested_date, graceTime, emp_pool, att_utility_pool, current_time)

        res_ids = []
        res_check_in = []
        for i in att_summary["late"]:
            res_ids.append(i.employeeId)

        if res_ids:
            query = """select min(check_in) from hr_attendance 
                       where employee_id in %s and duty_date=%s
                       group by employee_id"""
            self._cr.execute(query, tuple([tuple(res_ids),requested_date]))
            res_check_in = [x[0] for x in self._cr.fetchall()]


        if res_check_in:
            return {
                'name': ('Late Employee'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'hr.attendance',
                'domain': [('employee_id','in',res_ids),('check_in', 'in', res_check_in)],
                'view_id': [view.id],
                'context': {'create': False, 'edit': False},
                'type': 'ir.actions.act_window',
                'target':'new'
            }
