from odoo import api, fields, models, _
import datetime
from datetime import timedelta


class HrAttendanceErrorSummaryReport(models.AbstractModel):
    _name = 'report.gbs_hr_attendance_report.report_att_error_summary'

    get_dept_query = """SELECT DISTINCT(d.id),d.name, d.sequence FROM hr_employee e
                           JOIN hr_department d ON d.id = e.department_id
                           WHERE e.operating_unit_id = %s
                           ORDER BY d.sequence ASC"""

    get_non_management_emp_att_query = """SELECT 
                                                (check_in + interval '6h') AS check_in, 
                                                (check_out + interval '6h') AS check_out
                                          FROM hr_attendance
                                          WHERE 	
                                                employee_id = %s AND has_error = True AND
                                                ((
                                                (check_out = NULL AND DATE(check_in) BETWEEN %s AND %s) OR
                                                (DATE(check_out) BETWEEN %s AND %s)
                                                ) OR (
                                                (check_in = NULL AND DATE(check_out) BETWEEN %s AND %s) OR
                                                (DATE(check_in) BETWEEN %s AND %s)
                                                ))
                                           ORDER BY CASE 
                                                WHEN(check_in IS NOT NULL) THEN check_in 
                                                WHEN(check_out IS NOT NULL) THEN check_out END ASC"""




    @api.multi
    def render_html(self, docids, data=None):

        # requested_date = data['required_date']
        # curr_time_gmt = datetime.datetime.now()
        # current_time = curr_time_gmt + timedelta(hours=6)

        att_utility_pool = self.env['attendance.utility']

        from_date = att_utility_pool.getDateFromStr(data['from_date'])
        to_date = att_utility_pool.getDateFromStr(data['to_date'])

        data_list = []
        attendance_list_by_emp = []

        if data['type'] == "unit_type":

            data['department_name'] = "All"

            self._cr.execute(self.get_dept_query, tuple([data['operating_unit_id']]))
            deptList = self._cr.fetchall()

            for dept in deptList:

                dpt_wise_emp = {}
                dpt_wise_emp['name'] = dept[1]
                dpt_wise_emp['seq'] = dept[2]
                dpt_wise_emp['val'] = []

                empList = self.env['hr.employee'].search(['&',('department_id', '=', dept[0]),
                                                          ('operating_unit_id', '=', data['operating_unit_id'])], order='employee_sequence asc')
                for emp in empList:
                    attendance_list_by_emp = self.getErrorAtt(emp, from_date, to_date, att_utility_pool)
                    if len(attendance_list_by_emp) > 0:
                        dpt_wise_emp['val'].extend(attendance_list_by_emp)
                data_list.append(dpt_wise_emp)

        elif data['type'] == "department_type":


            dpt_wise_emp = {}
            dpt_wise_emp['name'] = data['department_name']
            dpt_wise_emp['seq'] = 0
            dpt_wise_emp['val'] = []
            empList = self.env['hr.employee'].search([('department_id', '=', data['department_id'])],
                                                     order='employee_sequence asc')
            for emp in empList:
                attendance_list_by_emp = self.getErrorAtt(emp, from_date, to_date, att_utility_pool)
                if len(attendance_list_by_emp) > 0:
                    dpt_wise_emp['val'].extend(attendance_list_by_emp)
            data_list.append(dpt_wise_emp)

        elif data['type'] == "employee_type":

            dpt_wise_emp = {}
            dpt_wise_emp['seq'] = 0
            dpt_wise_emp['val'] = []

            emp = self.env['hr.employee'].search([('id', '=', data['emp_id'])])
            dpt_wise_emp['name'] = emp.department_id.name

            attendance_list_by_emp = self.getErrorAtt(emp, from_date, to_date, att_utility_pool)
            if len(attendance_list_by_emp) > 0:
                dpt_wise_emp['val'].extend(attendance_list_by_emp)

            data_list.append(dpt_wise_emp)


        docargs = {
            'data': data,
            'data_list': data_list,
            'data_list_len': 7,
        }

        return self.env['report'].render('gbs_hr_attendance_report.report_att_error_summary', docargs)


    def getErrorAtt(self, emp, fromDate, toDate, att_utility_pool):

        day = datetime.timedelta(days=1)

        fdt = fromDate - day
        tdt = toDate + day

        attendance_list = []
        if emp.is_monitor_attendance == False:
            return attendance_list

        self._cr.execute(self.get_non_management_emp_att_query, tuple([emp.id, fdt, tdt, fdt, tdt,
                                                                       fdt, tdt, fdt, tdt]))
        attList = self._cr.fetchall()

        for attendance in attList:
            attendance_list.append(self.buildNonManagementEmployee(emp, attendance))

        return attendance_list



    #
    # def getErrorAtt(self, emp, fromDate, toDate, att_utility_pool):
    #
    #     day = datetime.timedelta(days=1)
    #
    #     fdt = fromDate - day
    #     tdt = toDate + day
    #
    #     attendance_list = []
    #     if emp.is_monitor_attendance == False:
    #         return attendance_list
    #
    #     if emp.is_executive == False:
    #         # For non-management employee
    #         self._cr.execute(self.get_non_management_emp_att_query, tuple([emp.id, fdt, tdt, fdt, tdt,
    #                                                                        fdt, tdt, fdt, tdt]))
    #         attList = self._cr.fetchall()
    #
    #         for attendance in attList:
    #             attendance_list.append(self.buildNonManagementEmployee(emp,attendance))
    #
    #     elif emp.is_executive == True:
    #
    #         # For management employee
    #         dutyTimeMap = att_utility_pool.getDutyTimeByEmployeeId(emp.id, fdt, tdt)
    #         currDate = fromDate
    #
    #         while currDate <= toDate:
    #
    #             if dutyTimeMap.get(att_utility_pool.getStrFromDate(currDate)):
    #                 attendanceList = att_utility_pool.getErrorAttendanceListByDay(emp.id, currDate, day, dutyTimeMap)
    #                 outcome = self.buildManagementEmployee(emp, attendanceList)
    #                 if len(outcome) > 0:
    #                     attendance_list.append(outcome)
    #
    #             currDate = currDate + day
    #
    #     return attendance_list



    def buildManagementEmployee(self, emp, attendanceList):

        emp_obj = {}
        if len(attendanceList) == 0:
            return emp_obj

        if attendanceList[0][0] != None and attendanceList[len(attendanceList)-1][1] != None:
            return emp_obj


        emp_obj['name'] = emp.name
        emp_obj['acc_no'] = emp.device_employee_acc
        emp_obj['designation'] = emp.job_id.name
        emp_obj['check_in'] = attendanceList[0][0]
        emp_obj['check_out'] = attendanceList[len(attendanceList)-1][1]
        if emp.is_executive == True:
            emp_obj['is_executive'] = "Management"
        else:
            emp_obj['is_executive'] = "Non-Management"
        return emp_obj


    def buildNonManagementEmployee(self, emp, attendance):

        emp_obj = {}
        emp_obj['name'] = emp.name
        emp_obj['acc_no'] = emp.device_employee_acc
        emp_obj['designation'] = emp.job_id.name
        emp_obj['check_in'] = attendance[0]
        emp_obj['check_out'] = attendance[1]
        if emp.is_executive == True:
            emp_obj['is_executive'] = "Management"
        else:
            emp_obj['is_executive'] = "Non-Management"
        return emp_obj