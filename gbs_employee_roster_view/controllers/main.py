from odoo import fields, http, _
from odoo.http import request
import datetime
import json
from bson import json_util

class emp_roster(http.Controller):


    def getDateFromStr(self, dateStr):
        if dateStr:
            return datetime.datetime.strptime(dateStr, "%m/%d/%Y")
        else:
            return datetime.datetime.now()

    @http.route(['/employee/roster'], type='json', auth="user")
    def update(self, type=None, operating_unit_id=None, department_id=None, employee_id=None,
               from_date=None, to_date=None,  **post):

        employee_pool = request.env['hr.employee']
        att_utility_pool = request.env['attendance.utility']

        fromDate = self.getDateFromStr(from_date)
        toDate = self.getDateFromStr(to_date)

        if int(employee_id) > 0:
            emp_list = employee_pool.search([('id', '=', employee_id), ('active', '=', True)])
        elif int(department_id) > 0:
            emp_list = employee_pool.search([('operating_unit_id', '=', operating_unit_id),
                                             ('department_id', '=', department_id),
                                             ('active', '=', True)],
                                            order='job_id desc')
        else:
            emp_list = employee_pool.search([('operating_unit_id', '=', operating_unit_id),
                                             ('active', '=', True)],
                                             order='department_id desc, job_id desc')

        data_list = []
        day = datetime.timedelta(days=1)

        for emp in emp_list:

            dutyTimeMap = att_utility_pool.getDutyTimeByEmployeeId(emp.id, fromDate, toDate)
            alterTimeMap = att_utility_pool.buildAlterDutyTime(fromDate, fromDate, emp.id)
            currDate = fromDate
            while currDate <= toDate:

                if alterTimeMap.get(att_utility_pool.getStrFromDate(currDate)):  # Check this date is alter date
                    alterDayDutyTime = alterTimeMap.get(att_utility_pool.getStrFromDate(currDate))

                    data_list.append(self.buildDutyDate(emp, alterDayDutyTime, 2))

                elif dutyTimeMap.get(att_utility_pool.getStrFromDate(currDate)):
                    currentDaydutyTime = dutyTimeMap.get(att_utility_pool.getStrFromDate(currDate))

                    data_list.append(self.buildDutyDate(emp, currentDaydutyTime, 1))

                currDate = currDate + day

        return json.dumps(data_list, default=json_util.default)

    def buildDutyDate(self, emp, dutyTime, dutyType):

        row_obj = {}
        row_obj['name'] = emp.name + "[" + str(emp.device_employee_acc) + "]"

        row_obj['startDutyTime'] = str(dutyTime.startDutyTime)
        row_obj['endDutyTime'] = str(dutyTime.endDutyTime)

        if dutyTime.startDutyTime != 0 and dutyTime.endDutyTime != 0:
            row_obj['dutyTime'] = (dutyTime.endDutyTime - dutyTime.startDutyTime).total_seconds() / 3600
        else:
            row_obj['dutyTime'] = 0

        row_obj['otStartDutyTime'] = str(dutyTime.otStartDutyTime)
        row_obj['otEndDutyTime'] = str(dutyTime.otEndDutyTime)
        if dutyTime.otStartDutyTime != 0 and dutyTime.otEndDutyTime != 0:
            row_obj['otDutyTime'] = (dutyTime.otEndDutyTime - dutyTime.otStartDutyTime).total_seconds() / 3600
        else:
            row_obj['otDutyTime'] = 0

        row_obj['type'] = dutyType

        return row_obj