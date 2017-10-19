from openerp import models, fields
import datetime


MAX_ATTEMPT_TO_SUCCESS = 5


class AttendanceErrorDataProcessor(models.Model):
    _name = 'hr.attendance.error.data.temp'

    get_distinct_employee = """select distinct employee_id from hr_attendance
                                    where attempt_set_duty_date <= %s
                                    and duty_date IS NULL
                                    and operating_unit_id = %s
                                    order by employee_id asc"""

    def doErrorToSuccess(self):

        hr_employee_pool = self.env['hr.employee']

        hr_att_error_pool = self.env['hr.attendance.import.error']
        errorDataList = hr_att_error_pool.search([('attempt_to_success', '<=', MAX_ATTEMPT_TO_SUCCESS),
                                                  ('import_id', '=', None)], order='id asc')
        for row in errorDataList:
            if row.employee_code:
                emp = hr_employee_pool.search([('device_employee_acc', '=', row.employee_code)], limit=1)
                if emp:
                    self.processErrorData(row, emp.id)
                    row.unlink()
                else:
                    row.write({'attempt_to_success': row.attempt_to_success + 1})

            else:
                row.write({'attempt_to_success': row.attempt_to_success + 1})

    def processErrorData(self, row, employeeId):

        hr_att_pool = self.env['hr.attendance']

        if row.check_in:
            preAttData = hr_att_pool.search([('employee_id', '=', employeeId),
                                             ('check_out', '!=', False)], limit=1, order='check_out asc')

            if preAttData and preAttData.check_in is False:
                chk_out = self.getDateTimeFromStr(preAttData.check_out)
                durationInHour = (chk_out - self.getDateTimeFromStr(row.check_in)).total_seconds() / 60 / 60
                if durationInHour <= 15 and durationInHour >= 0:
                    preAttData.write({'check_in': self.getDateTimeFromStr(row.check_in),
                                      'worked_hours': durationInHour,
                                      'write_date': datetime.datetime.now(),
                                      'has_error': False,
                                      'operating_unit_id': row.operating_unit_id})
                else:
                    self.createDataFromError(row, employeeId, hr_att_pool)
            else:
                self.createDataFromError(row, employeeId, hr_att_pool)
            # self.createDataFromError(row, employeeId, hr_att_pool)
        elif row.check_out:

            preAttData = hr_att_pool.search([('employee_id', '=', employeeId),
                                             ('check_in', '!=', False)], limit=1, order='check_in desc')

            if preAttData and preAttData.check_out is False:
                chk_in = self.getDateTimeFromStr(preAttData.check_in)
                durationInHour = (self.getDateTimeFromStr(row.check_out) - chk_in).total_seconds() / 60 / 60
                if durationInHour <= 15 and durationInHour >= 0:
                    preAttData.write({'check_out': self.getDateTimeFromStr(row.check_out),
                                      'worked_hours': durationInHour,
                                      'write_date': datetime.datetime.now(),
                                      'has_error': False,
                                      'operating_unit_id': row.operating_unit_id})
                else:
                    self.createDataFromError(row, employeeId, hr_att_pool)
            else:
                self.createDataFromError(row, employeeId, hr_att_pool)

    def createDataFromError(self, row, employeeId, hr_att_pool):

        if row.check_in:
            create_vals = {'employee_id': employeeId,
                           'check_in': self.getDateTimeFromStr(row.check_in),
                           'create_date': datetime.datetime.now(),
                           'write_date': datetime.datetime.now(),
                           'has_error': True,
                           'manual_attendance_request': False,
                           'is_system_generated': True,
                           'operating_unit_id': row.operating_unit_id}
        else:
            create_vals = {'employee_id': employeeId,
                           'check_in': None,
                           'check_out': self.getDateTimeFromStr(row.check_out),
                           'create_date': datetime.datetime.now(),
                           'write_date': datetime.datetime.now(),
                           'has_error': True,
                           'manual_attendance_request': False,
                           'is_system_generated': True,
                           'operating_unit_id': row.operating_unit_id}

        res = hr_att_pool.create(create_vals)



    def setDutyDate(self, operating_unit_id):

        hr_att_pool = self.env['hr.attendance']
        att_utility_pool = self.env['attendance.utility']

        day = datetime.timedelta(days=1)

        startDate = datetime.datetime(2017, 05, 23)
        endDate = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        att_list = hr_att_pool.search([('attempt_set_duty_date', '<=', MAX_ATTEMPT_TO_SUCCESS),
                                       ('duty_date', '=', None),
                                       ('check_in', '!=', None),
                                       ('operating_unit_id', '=', operating_unit_id)], order='employee_id, check_in ASC')

        # , limit = 3000
        if att_list:
            self.setDutyDateByEmployee(startDate, endDate, att_list, day, att_utility_pool)



    def setDutyDateByEmployee(self, startDate, endDate, att_list, day, att_utility_pool):

        employeeId = att_list[0].employee_id.id
        preStartDate = startDate - day
        postEndDate = endDate + day

        dutyTimeMap = {}
        shiftList = []

        dutyTimeMap = att_utility_pool.getDutyTimeByEmployeeId(employeeId, preStartDate, postEndDate)
        alterTimeMap = att_utility_pool.buildAlterDutyTime(startDate, endDate, employeeId)


        for attendance in att_list:

            if employeeId != attendance.employee_id.id:
                # Get Next Employee Duty Schedule
                employeeId = attendance.employee_id.id
                dutyTimeMap = att_utility_pool.getDutyTimeByEmployeeId(employeeId, preStartDate, postEndDate)
                alterTimeMap = att_utility_pool.buildAlterDutyTimeForDailyAtt(startDate, endDate, employeeId)


            att_date = att_utility_pool.convertStrDateTimeInc(attendance.check_in)

            if alterTimeMap.get(att_utility_pool.getStrFromDate(att_date)): # Check this date is alter date
                alterDayDutyTime = alterTimeMap.get(att_utility_pool.getStrFromDate(att_date))
                self.updateAttendanceByDay(attendance, att_date, alterDayDutyTime, day, dutyTimeMap, att_utility_pool)
            elif dutyTimeMap.get(att_utility_pool.getStrFromDate(att_date)):
                currentDaydutyTime = dutyTimeMap.get(att_utility_pool.getStrFromDate(att_date))
                self.updateAttendanceByDay(attendance, att_date, currentDaydutyTime, day, dutyTimeMap, att_utility_pool)
            elif dutyTimeMap.get(att_utility_pool.getStrFromDate(att_date - day)):
                # This logic for : When Schedule Check In 2017-10-16:22:00 & Schedule Check OUT 2017-10-17:07:00.
                # At this time If user Check In at 2017-10-17:06:00, Then Duty Date will set by 2017-10-16
                currentDaydutyTime = dutyTimeMap.get(att_utility_pool.getStrFromDate(att_date - day))
                self.updateAttendanceByDay(attendance, att_date - day, currentDaydutyTime, day, dutyTimeMap, att_utility_pool)
            else:
                attendance.write({'attempt_set_duty_date': attendance.attempt_set_duty_date + 1})


    def getDateTimeFromStr(self, dateStr):
        if dateStr:
            return datetime.datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
        else:
            return None

    # def updateAttendanceByDay(self, attendance, currDate, currentDaydutyTime, day, dutyTimeMap,
    #                           att_utility_pool):
    #
    #     previousDayDutyTime = att_utility_pool.getPreviousDutyTime(currDate - day, dutyTimeMap)
    #     nextDayDutyTime = att_utility_pool.getNextDutyTime(currDate + day, dutyTimeMap)
    #
    #     if previousDayDutyTime.endActualDutyTime < att_utility_pool.convertStrDateTimeInc(
    #             attendance.check_in) < currentDaydutyTime.endActualDutyTime and (
    #             attendance.check_out == False or
    #                 currentDaydutyTime.startDutyTime < att_utility_pool.convertStrDateTimeInc(
    #                 attendance.check_out) < nextDayDutyTime.startDutyTime):
    #         attendance.write({'duty_date': currDate})
    #     else:
    #         attendance.write({'attempt_set_duty_date': attendance.attempt_set_duty_date + 1})






    def updateAttendanceByDay(self, attendance, currDate, currentDaydutyTime, day, dutyTimeMap, att_utility_pool):

        previousDayDutyTime = att_utility_pool.getPreviousDutyTime(currDate - day, dutyTimeMap)
        nextDayDutyTime = att_utility_pool.getNextDutyTime(currDate + day, dutyTimeMap)

        if previousDayDutyTime.endActualDutyTime < att_utility_pool.convertStrDateTimeInc(
                attendance.check_in) < currentDaydutyTime.endActualDutyTime and ( attendance.check_out == False or
                                currentDaydutyTime.startDutyTime < att_utility_pool.convertStrDateTimeInc(
                            attendance.check_out) < nextDayDutyTime.startDutyTime):
            attendance.write({'duty_date': currDate})
        else:
            # This logic for : When Schedule Check In 2017-10-16:22:00 & Schedule Check OUT 2017-10-17:07:00.
            # At this time If user Check In at 2017-10-17:06:00, Then Duty Date will set by 2017-10-16
            preDate = currDate - day
            dt = att_utility_pool.getStrFromDate(preDate)
            if dutyTimeMap.get(dt):
                currDaydutyTime = dutyTimeMap.get(dt)
                previousDayDutyTime2 = att_utility_pool.getPreviousDutyTime(preDate - day, dutyTimeMap)
                nextDayDutyTime2 = att_utility_pool.getNextDutyTime(preDate + day, dutyTimeMap)

                if previousDayDutyTime2.endActualDutyTime < att_utility_pool.convertStrDateTimeInc(
                        attendance.check_in) < currDaydutyTime.endActualDutyTime and (
                        attendance.check_out == False or
                            currDaydutyTime.startDutyTime < att_utility_pool.convertStrDateTimeInc(
                            attendance.check_out) < nextDayDutyTime2.startDutyTime):
                    attendance.write({'duty_date': preDate})
                else:
                    attendance.write({'attempt_set_duty_date': attendance.attempt_set_duty_date + 1})
            else:
                attendance.write({'attempt_set_duty_date': attendance.attempt_set_duty_date + 1})



