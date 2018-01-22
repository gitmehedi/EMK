from odoo import api, fields, models, _
import datetime
from datetime import timedelta

class HrAttendanceErrorSummaryReport(models.AbstractModel):
    _name = 'report.hr_overtime_report.overtime_summary_report'

    getExtraOTQuery = """SELECT 
                              DATE(from_datetime + interval '6h'), 
                              (from_datetime + interval '6h'),
                              (to_datetime + interval '6h')
                         FROM 
                              hr_ot_requisition 
                         WHERE 
                            DATE(from_datetime + interval '6h') BETWEEN %s AND %s AND 
                            state = 'approved' AND 
                            employee_id = %s"""


    @api.multi
    def render_html(self, docids, data=None):

        report_obj = self.env['report']

        day = datetime.timedelta(days=1)
        data_list = []

        att_utility_pool = self.env['attendance.utility']

        from_date = att_utility_pool.getDateFromStr(data['from_date'])
        to_date = att_utility_pool.getDateFromStr(data['to_date'])

        currDate = from_date

        employeeId = data['emp_id']

        emp = self.env['hr.employee'].search([('id', '=', data['emp_id'])])

        dutyTimeMap = att_utility_pool.getDutyTimeByEmployeeId(employeeId, from_date, to_date)
        alterTimeMap = att_utility_pool.buildAlterDutyTime(from_date, to_date, employeeId)

        while currDate <= to_date:

            if alterTimeMap.get(att_utility_pool.getStrFromDate(currDate)):  # Check this date is alter date
                alterDayDutyTime = alterTimeMap.get(att_utility_pool.getStrFromDate(currDate))

                if alterDayDutyTime.otStartDutyTime and alterDayDutyTime.otEndDutyTime:

                    data_list.append(self.buildOt(currDate, alterDayDutyTime.otStartDutyTime,
                                                  alterDayDutyTime.otEndDutyTime, "Alter Duty OT"))

            elif dutyTimeMap.get(att_utility_pool.getStrFromDate(currDate)):
                currentDaydutyTime = dutyTimeMap.get(att_utility_pool.getStrFromDate(currDate))

                if currentDaydutyTime.otStartDutyTime and currentDaydutyTime.otEndDutyTime:

                    data_list.append(self.buildOt(currDate, currentDaydutyTime.otStartDutyTime,
                                                  currentDaydutyTime.otEndDutyTime, "Schedule OT"))

            currDate = currDate + day

        #For Extra OT Hrs
        self._cr.execute(self.getExtraOTQuery, (from_date, to_date, employeeId))
        get_query_extra_ot = self._cr.fetchall()
        if get_query_extra_ot:
            for get_ot in get_query_extra_ot:
                data_list.append(self.buildOt(att_utility_pool.getDateFromStr(get_ot[0]), att_utility_pool.getDateTimeFromStr(get_ot[1]),
                                              att_utility_pool.getDateTimeFromStr(get_ot[2]), "Extra OT"))

        data_list = sorted(data_list, key=lambda k: k['from_date'])

        docargs = {
            'data': data,
            'data_list':data_list,
        }
        return report_obj.render('hr_overtime_report.overtime_summary_report', docargs)


    def buildOt(self, dt, from_date, to_date, note):
        row_obj = {}
        row_obj['date'] = dt
        row_obj['from_date'] = from_date
        row_obj['to_date'] = to_date
        row_obj['hours'] = (to_date - from_date).total_seconds() / 3600
        row_obj['note'] = note
        return row_obj
