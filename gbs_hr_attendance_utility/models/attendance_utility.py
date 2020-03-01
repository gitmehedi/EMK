from odoo import api, fields, models,tools
import datetime
from datetime import timedelta
from utility_class import Shift,ShiftLine,DutyTime,TempLateTime,Employee


class AttendanceUtility(models.TransientModel):
    _name = "attendance.utility"
    # _auto = False

    employee_shift_history_query = """SELECT effective_from, shift_id
                                    FROM hr_shifting_history
                                    WHERE employee_id = %s AND (%s BETWEEN effective_from AND effective_end
                                    OR %s BETWEEN effective_from AND effective_end
                                    OR (%s <= effective_from AND effective_end <= %s))
                                    ORDER BY effective_from ASC"""

    daily_attendance_query = """SELECT (check_in + interval '6h') AS check_in, (check_out + interval '6h') AS check_out, worked_hours
                                        FROM hr_attendance
                                      WHERE employee_id = %s AND check_in between %s and %s AND (check_out IS NULL OR check_out > %s)
                                      ORDER BY check_in ASC LIMIT 1"""

    alter_attendance_query = """SELECT (check_in + interval '6h') AS check_in, 
                                    (check_out + interval '6h') AS check_out, 
                                    worked_hours, 1 AS att_type
                                    FROM hr_attendance
                                WHERE (check_in BETWEEN %s AND %s) AND (check_out BETWEEN %s AND %s) AND employee_id = %s
                                UNION
                                SELECT (check_in + interval '6h') AS check_in, 
                                   (check_out + interval '6h') AS check_out, 
                                   0 AS worked_hours, 2 AS att_type
                                FROM hr_manual_attendance 
                                WHERE state = 'validate' AND sign_type = 'both' AND 
                                      (check_in BETWEEN %s AND %s) AND (check_out BETWEEN %s AND %s) AND employee_id = %s
                                UNION
                                SELECT (date_from + interval '6h') AS check_in, 
                                   (date_to + interval '6h') AS check_out, 
                                   0 AS worked_hours, 3 AS att_type      
                                FROM hr_short_leave 
                                WHERE state = 'validate' AND 
                                (date_from BETWEEN %s AND %s) AND (date_to BETWEEN %s AND %s) AND employee_id = %s
                                ORDER BY check_in, att_type ASC"""

    error_attendance_for_management_emp = """SELECT 
                                                (check_in + interval '6h') AS check_in, 
                                                (check_out + interval '6h') AS check_out
                                              FROM hr_attendance
                                              WHERE 	
                                                employee_id = %s AND
                                                ((
                                                (check_out = NULL AND DATE(check_in + interval '6h') = DATE(%s)) OR
                                                (DATE(check_out + interval '6h') = DATE(%s))
                                                ) OR (
                                                (check_in = NULL AND DATE(check_out + interval '6h') = DATE(%s)) OR
                                                (DATE(check_in + interval '6h') = DATE(%s))
                                                ))
                                               ORDER BY CASE 
                                                WHEN(check_in IS NOT NULL) THEN check_in 
                                                WHEN(check_out IS NOT NULL) THEN check_out END ASC"""


    def getDutyTimeByEmployeeId(self, employeeId, preStartDate, postEndDate):
        # Getting Shift Ids for an employee
        self._cr.execute(self.employee_shift_history_query, (employeeId, preStartDate, postEndDate, preStartDate, postEndDate))
        calendarList = self._cr.fetchall()
        shiftList = self.getShiftList(calendarList, postEndDate)
        dutyTimeMap = self.buildDutyTime(preStartDate, postEndDate, shiftList)
        # self.printDutyTime(preStartDate, postEndDate, dutyTimeMap)
        return dutyTimeMap

    def getHolidayAlwByEmployee(self, employeeID, fromDate, toDate):
        result = {}

        lines = self.env['hr.holiday.allowance.line'].search([('emp_allowance_date', '>=', fromDate),
                                                             ('emp_allowance_date', '<=', toDate),
                                                             ('state', '=', 'approved'),
                                                             ('employee_id', '=', employeeID)])
        if lines:
            for l in lines:
                result[l.emp_allowance_date] = True

        return result

    def isSetRosterByEmployeeId(self, employeeId, preStartDate, postEndDate):
        # Getting Shift Ids for an employee
        self._cr.execute(self.employee_shift_history_query, (employeeId, preStartDate, postEndDate, preStartDate, postEndDate))
        calendarList = self._cr.fetchall()
        if calendarList:
            return True
        else:
            return False


    def buildAlterDutyTime(self,startDate, endDate, employeeId):
        att_query = """SELECT alter_date, (duty_start+ interval '6h') AS duty_start,
                        (duty_end+ interval '6h') AS duty_end,
                        is_included_ot, (ot_start+ interval '6h') AS ot_start,
                         (ot_end+ interval '6h') AS ot_end, grace_time
                        FROM hr_shift_alter
                        WHERE employee_id = %s AND state = 'approved' AND
                        alter_date BETWEEN %s AND %s
                        ORDER BY alter_date ASC"""
        self._cr.execute(att_query, (employeeId,startDate,endDate))
        alterLines = self._cr.fetchall()
        alterTimeMap = {}
        for i, alter in enumerate(alterLines):
            alterTimeMap[self.getStrFromDate(self.getDateFromStr(alter[0]))] = DutyTime(self.getDateTimeFromStr(alter[1]),
                                                                            self.getDateTimeFromStr(alter[2]),
                                                                            alter[3], self.getDateTimeFromStr(alter[4]),
                                                                            self.getDateTimeFromStr(alter[5]), alter[6])

        return alterTimeMap

    def getDailyAttByDateAndUnit(self, requestedDate, operating_unit_id):
        att_query = """SELECT employee_id, MIN(check_in) + interval '6h' AS check_in FROM hr_attendance att
                        JOIN hr_employee emp ON emp.id = att.employee_id
                        WHERE duty_date = %s AND emp.operating_unit_id = %s
                        GROUP BY employee_id ORDER BY employee_id"""
        self._cr.execute(att_query, (requestedDate, operating_unit_id))
        attLines = self._cr.fetchall()
        employeeAttMap = {}
        for i, att in enumerate(attLines):
            employeeAttMap[att[0]] = self.getDateTimeFromStr(att[1])

        return employeeAttMap

    def getDailyAttByDateAndDept(self, requestedDate, dept_id):
        att_query = """SELECT employee_id, MIN(check_in) + interval '6h' AS check_in FROM hr_attendance att
                        JOIN hr_employee emp ON emp.id = att.employee_id
                        WHERE duty_date = %s AND emp.department_id = %s
                        GROUP BY employee_id ORDER BY employee_id"""
        self._cr.execute(att_query, (requestedDate, dept_id))
        attLines = self._cr.fetchall()
        employeeAttMap = {}
        for i, att in enumerate(attLines):
            employeeAttMap[att[0]] = self.getDateTimeFromStr(att[1])

        return employeeAttMap


    def buildAlterDutyTimeForDailyAtt(self,startDate, endDate, employeeId):
        att_query = """SELECT alter_date, (duty_start+ interval '6h') AS duty_start,
                        (duty_end+ interval '6h') AS duty_end,
                        is_included_ot, (ot_start+ interval '6h') AS ot_start,
                         (ot_end+ interval '6h') AS ot_end, grace_time
                        FROM hr_shift_alter
                        WHERE employee_id = %s AND state = 'approved' AND
                        alter_date BETWEEN %s AND %s
                        ORDER BY alter_date ASC"""
        self._cr.execute(att_query, (employeeId,startDate,endDate))
        alterLines = self._cr.fetchall()
        alterTimeMap = {}
        for i, alter in enumerate(alterLines):
            alterTimeMap[self.getStrFromDate(self.getDateTimeFromStr(alter[1]).date())] = DutyTime(self.getDateTimeFromStr(alter[1]),
                                                                            self.getDateTimeFromStr(alter[2]),
                                                                            alter[3], self.getDateTimeFromStr(alter[4]),
                                                                            self.getDateTimeFromStr(alter[5]), alter[6])

        return alterTimeMap

    def printDutyTime(self, preStartDate, postEndDate, dutyTimeMap):
        day = datetime.timedelta(days=1)
        print ">>>>>>>>>>>>>>>>>> For Test Data >>>>>>>>>>>>>>>>>"
        while preStartDate <= postEndDate:
            dt = dutyTimeMap.get(preStartDate.strftime('%Y.%m.%d'))
            if dt:
                print (
                preStartDate.strftime('%Y.%m.%d'), "Start:", dt.startDutyTime.strftime('%Y.%m.%d-%H:%M:%S'), "End:",
                dt.endDutyTime.strftime('%Y.%m.%d-%H:%M:%S'), "Diff:", dt.dutyMinutes / 60, dt.graceTime)
            preStartDate = preStartDate + day
        print ">>>>>>>>>>>>>>>>>> End For Test Data >>>>>>>>>>>>>>>>>"

    def getAttendanceDataForDailyAtt(self, dutyTimeMap, employeeId, preStartDate, postEndDate):
        dutyTime_s = dutyTimeMap.get(self.getStrFromDate(preStartDate))
        if dutyTime_s:
            att_time_pre_end = dutyTime_s.endDutyTime
        else:
            att_time_pre_end = preStartDate + timedelta(hours=23)

        dutyTime_e = dutyTimeMap.get(self.getStrFromDate(postEndDate))
        if dutyTime_e:
            att_time_post_start = dutyTime_e.startDutyTime
            att_time_post_end = dutyTime_e.endDutyTime
        else:
            att_time_post_start = postEndDate + timedelta(hours=1)
            att_time_post_end = postEndDate + timedelta(hours=1)

        self._cr.execute(self.daily_attendance_query, (employeeId, att_time_pre_end, att_time_post_end,att_time_post_start))


        attendance_data = self._cr.fetchall()

        return attendance_data

    def getAttendanceListByAlterDay(self, alterDayDutyTime, day, dutyTimeMap, employeeId):
        attendanceDayList = []

        preEndActualDutyTime = self.convertDateTime(alterDayDutyTime.startDutyTime - timedelta(hours=4))
        endActualDuty = self.convertDateTime(alterDayDutyTime.endActualDutyTime)
        startDutyTime = self.convertDateTime(alterDayDutyTime.startDutyTime)
        nextStartDutyTime = self.convertDateTime(alterDayDutyTime.endActualDutyTime + timedelta(hours=4))

        self._cr.execute(self.alter_attendance_query, (preEndActualDutyTime, endActualDuty, startDutyTime, nextStartDutyTime,employeeId,
                                                       preEndActualDutyTime, endActualDuty, startDutyTime, nextStartDutyTime, employeeId,
                                                       preEndActualDutyTime, endActualDuty, startDutyTime, nextStartDutyTime, employeeId))
        attendance_line = self._cr.fetchall()

        for i, attendance in enumerate(attendance_line):
            att_check_in = attendance[0]
            att_check_out = attendance[1]

            chk_in = self.getDateTimeFromStr(att_check_in)
            chk_out = self.getDateTimeFromStr(att_check_out)

            # Adjust Check_in Check_out time within atutomated, manual and short leave
            if i > 0 and attendance[3] > 1:
                pre_chk_out = self.getDateTimeFromStr(attendance_line[i - 1][1])
                if pre_chk_out > chk_in:
                    chk_in = pre_chk_out
                    att_check_in = attendance_line[i - 1][1]

            if i < (len(attendance_line) - 1) and attendance[3] > 1:
                next_chk_in = self.getDateTimeFromStr(attendance_line[i + 1][0])
                if next_chk_in < chk_out:
                    chk_out = next_chk_in
                    att_check_out = attendance_line[i + 1][0]

            duration = (chk_out - chk_in).total_seconds() / 60 / 60
            attendanceDayList.append(TempLateTime(att_check_in, att_check_out, duration))
        return attendanceDayList

    def getErrorAttendanceListByDay(self, employeeId, currDate, day, dutyTimeMap):

        previousDayDutyTime = self.getPreviousDutyTime(currDate - day, dutyTimeMap)
        nextDayDutyTime = self.getNextDutyTime(currDate + day, dutyTimeMap)

        self._cr.execute(self.error_attendance_for_management_emp,
                         tuple([employeeId, currDate, currDate, currDate, currDate]))

        attendanceDayList = self._cr.fetchall()
        return attendanceDayList

    def getAttendanceListByDay(self, attendance_data, currDate, currentDaydutyTime, day, dutyTimeMap):

        attendanceDayList = []
        previousDayDutyTime = self.getPreviousDutyTime(currDate - day, dutyTimeMap)
        nextDayDutyTime = self.getNextDutyTime(currDate + day, dutyTimeMap)

        temp_attendance_data = list(attendance_data)

        for i, attendance in enumerate(attendance_data):

            att_check_in = attendance[0]
            att_check_out = attendance[1]

            chk_in = self.getDateTimeFromStr(att_check_in)
            chk_out = self.getDateTimeFromStr(att_check_out)

            #Adjust Check_in Check_out time within atutomated, manual and short leave
            if i > 0 and attendance[3] > 1:
                pre_chk_out = self.getDateTimeFromStr(attendance_data[i-1][1])
                if pre_chk_out > chk_in:
                    chk_in = pre_chk_out
                    att_check_in = attendance_data[i-1][1]

            if i < (len(attendance_data) -1) and attendance[3] > 1:
                next_chk_in = self.getDateTimeFromStr(attendance_data[i+1][0])
                if next_chk_in < chk_out:
                    chk_out = next_chk_in
                    att_check_out = attendance_data[i+1][0]

            chk_out_limit = nextDayDutyTime.startDutyTime

            if currentDaydutyTime.endActualDutyTime >= nextDayDutyTime.startDutyTime:
                chk_out_limit = currentDaydutyTime.endActualDutyTime + timedelta(hours= 1)

            if previousDayDutyTime.endActualDutyTime < chk_in < currentDaydutyTime.endActualDutyTime and \
                                    currentDaydutyTime.startDutyTime < chk_out < chk_out_limit:
                duration = (chk_out - chk_in).total_seconds() / 60 / 60
                attendanceDayList.append(TempLateTime(att_check_in, att_check_out, duration))
                temp_attendance_data.remove(attendance)
            # If attendance data is greater then 48 hours from current date (startDate) then call break.
            # Means rest of the attendance date are not illegible for current date. Break condition apply for better optimization
            elif (chk_in - currDate).total_seconds() / 60 / 60 > 48:
                break
        attendance_data = temp_attendance_data
        return attendanceDayList

    def getShiftList(self, calendarList, postEndDate):
        shiftList = []
        day = datetime.timedelta(days=1)

        for i, calendar in enumerate(calendarList):
            if (len(calendarList) == i + 1):
                shiftList.append(Shift(self.getDateFromStr(calendarList[i][0]), postEndDate,
                                       calendarList[i][1], self.getShiftLines(calendarList[i][1])))
            else:
                shiftList.append(Shift(self.getDateFromStr(calendarList[i][0]), self.getDateFromStr(calendarList[i + 1][0]) - day,
                                       calendarList[i][1], self.getShiftLines(calendarList[i][1])))

        return shiftList


    def getShiftLines(self, shiftId):

        cal_att_query = """SELECT dayofweek, hour_from, hour_to,
                            "isIncludedOt", ot_hour_from, ot_hour_to, grace_time
                            FROM
                                resource_calendar_attendance
                            WHERE
                                calendar_id = %s
                            ORDER BY dayofweek ASC, id DESC"""

        self._cr.execute(cal_att_query, (shiftId,))
        shiftLines = self._cr.fetchall()

        shiftLinesMap = {}

        for i, shiftLine in enumerate(shiftLines):
            shiftLinesMap[int(shiftLine[0])] = ShiftLine(int(shiftLine[0]), shiftLine[1], shiftLine[2], shiftLine[3],
                                                         shiftLine[4], shiftLine[5], shiftLine[6])
        return shiftLinesMap

    def buildDutyTime(self, preStartDate, postEndDate, shiftList):
        dutyTimeMap = {}

        if not shiftList:
            return dutyTimeMap

        day = datetime.timedelta(days=1)
        while preStartDate <= postEndDate:
            for i, shift in enumerate(shiftList):
                if shift.effectiveDtStr <= preStartDate <= shift.effectiveDtEnd:
                    shiftObj = shift.shiftLines.get(preStartDate.weekday())
                    if shiftObj:

                        # To build normal duty time
                        startTime = shiftObj.startTime
                        endTime = shiftObj.endTime
                        startDutyTime = preStartDate + timedelta(hours=startTime)
                        if startTime >= endTime:
                            endDutyTime = preStartDate + timedelta(hours=endTime + 24)
                        else:
                            endDutyTime = preStartDate + timedelta(hours=endTime)

                        # To build OT duty time
                        otStartDutyTime = 0
                        otEndDutyTime = 0
                        otStartTime = shiftObj.otStartTime
                        otEndTime = shiftObj.otEndTime
                        if shiftObj.isot is True:
                            if startTime >= otStartTime:
                                otStartDutyTime = preStartDate + timedelta(hours=otStartTime + 24)
                            else:
                                otStartDutyTime = preStartDate + timedelta(hours=otStartTime)

                            if startTime >= otEndTime:
                                otEndDutyTime = preStartDate + timedelta(hours=otEndTime + 24)
                            else:
                                otEndDutyTime = preStartDate + timedelta(hours=otEndTime)

                        dutyTimeMap[preStartDate.strftime('%Y.%m.%d')] = DutyTime(startDutyTime, endDutyTime, shiftObj.isot,
                                                                                  otStartDutyTime, otEndDutyTime, shiftObj.graceTime)
                        break
            preStartDate = preStartDate + day
        return dutyTimeMap

    def makeDecisionForADays(self, att_summary, employeeAttMap, currDate, currentDaydutyTime, employee, graceTime,
                             todayIsHoliday, compensatoryLeaveMap, oTMap):

        employeeId = employee.id
        check_in = employeeAttMap.get(employeeId)

        if check_in:

            isLate = self.isLateByInTime(check_in, currentDaydutyTime, graceTime)

            if isLate is True:  # Check Absent OR Late
                # Check this day is holiday or personal leave
                if self.checkOnHolidays(employeeId, todayIsHoliday, compensatoryLeaveMap, oTMap) is True:
                    att_summary["holidays"].append(Employee(employee))
                elif self.checkOnPersonalLeave(employeeId, currDate) is True:
                    att_summary["leave"].append(Employee(employee))
                elif self.checkShortLeave(employeeId, self.convertDateTime(currentDaydutyTime.startDutyTime)) is True:
                    att_summary["short_leave"].append(Employee(employee))
                elif isLate == True:
                    att_summary["late"].append(Employee(employee, check_in))

            else:
                att_summary["on_time_present"].append(Employee(employee, check_in))

        else:
            if self.checkOnHolidays(employeeId, todayIsHoliday, compensatoryLeaveMap, oTMap) is True:
                att_summary["holidays"].append(Employee(employee))
            elif self.checkOnPersonalLeave(employeeId, currDate) is True:
                att_summary["leave"].append(Employee(employee))
            elif self.checkShortLeave(employeeId, self.convertDateTime(currentDaydutyTime.startDutyTime)) is True:
                att_summary["short_leave"].append(Employee(employee))
            else:
                att_summary["absent"].append(Employee(employee))

        return att_summary

    # Get previous duty time. If previous duty time is null that means this day was weekend.
    # Then set a default time at previous day
    def getPreviousDutyTime(self, date, dutyTimeMap):
        previousDayDutyTime = dutyTimeMap.get(self.getStrFromDate(date))
        if previousDayDutyTime:
            return previousDayDutyTime
        else:
            previousDayDutyTime = DutyTime(date.replace(hour=22, minute=00), date.replace(hour=23, minute=00), False, 0, 0, 0)
            return previousDayDutyTime

    # Get next duty time. If previous duty time is null that means this day was weekend.
    # Then set a default time at previous day
    def getNextDutyTime(self, date, dutyTimeMap):
        nextDutyTime = dutyTimeMap.get(self.getStrFromDate(date))
        if nextDutyTime:
            return nextDutyTime
        else:
            nextDutyTime = DutyTime(date + timedelta(hours=23.9), date + timedelta(hours=23.95), False, 0, 0, 0)
            return nextDutyTime

    def convertDateTime(self, dateStr):
        if dateStr:
            return dateStr + timedelta(hours=-6)

    def convertStrDateTime(self, dateStr):
        if dateStr:
            return self.getDateTimeFromStr(dateStr) + timedelta(hours=-6)

    def convertStrDateTimeInc(self, dateStr):
        if dateStr:
            return self.getDateTimeFromStr(dateStr) + timedelta(hours=6)

    def getDateTimeFromStr(self, dateStr):
        if dateStr:
            return datetime.datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
        else:
            return None


    # Utility Methods
    def getDateFromStr(self, dateStr):
        if dateStr:
            return datetime.datetime.strptime(dateStr, "%Y-%m-%d")
        else:
            return datetime.datetime.now()

    def getStrFromDate(self, date):
        return date.strftime('%Y.%m.%d')

    def getStrFromDate2(self, date):
        return date.strftime('%Y-%m-%d')

    def getStrFromDateTime(self, date):
        return date.strftime('%Y-%m-%d %H:%M:%S')

            ### Short Leave Check Method
    def checkShortLeave(self, employeeId, datetime_sl):
        leave_pool=self.env['hr.short.leave'].search([('date_from', '<=', self.getStrFromDateTime(datetime_sl)),
                                                 ('date_to', '>=',self.getStrFromDateTime(datetime_sl)),
                                                 ('employee_id', '=', employeeId)])
        if leave_pool:
            return True
        else:
            return False

            ### Short Leave Duration
    def getShortLeaveDuration(self,datetime_sl):
        leave_pool = self.env['hr.short.leave'].search([('date_from', '<=', datetime_sl),
                                                        ('date_to', '>=', datetime_sl)])
        if leave_pool:
            start_dt = fields.Datetime.from_string(leave_pool.date_from)
            finish_dt = fields.Datetime.from_string(leave_pool.date_to)
            diff = finish_dt - start_dt
            mins = float(diff.total_seconds() / 60)
            return mins

    def isLateByInTime(self, check_in, currentDayDutyTime, graceTime):



        if check_in > currentDayDutyTime.startDutyTime:
            lateMinutes = (check_in - currentDayDutyTime.startDutyTime).total_seconds() / 60
            if lateMinutes > graceTime:
                return True
        return False


            ### Get Grace Time
    def getGraceTime(self,datetime_g):
        get_grace_time_query = """SELECT grace_time FROM hr_attendance_grace_time 
                                                             WHERE (%s between effective_from_date and effective_to_date) 
                                                             OR (%s >= effective_from_date AND effective_to_date IS NULL)"""
        self._cr.execute(get_grace_time_query, (datetime_g, datetime_g))
        grace_time = self._cr.fetchone()
        if grace_time:
            mins = grace_time[0] * 60
            return mins
        else:
            return 15.0

    def checkOnHolidays(self, employeeId, todayIsHoliday, compensatoryLeaveMap, oTMap):

        if todayIsHoliday == False:
            return False

        if compensatoryLeaveMap.get(employeeId):
            return False
        elif oTMap.get(employeeId):
            return False
        else:
            return True

    def checkOnPersonalLeave(self, employeeId, startDate):

        query_str = """SELECT COUNT(h.id) FROM hr_holidays h
                        LEFT JOIN hr_holidays_status hhs ON hhs.id = h.holiday_status_id
                        WHERE h.employee_id = %s AND h.type='remove' 
                        AND h.state IN ('validate1','validate') AND 
                        (hhs.unpaid IS NULL OR hhs.unpaid =FALSE) AND
                        %s BETWEEN h.date_from::DATE AND h.date_to::DATE"""

        self._cr.execute(query_str, (employeeId, startDate))
        count = self._cr.fetchall()
        if count[0][0] > 0:
            return True
        else:
            return False

    def checkOnUnpaidLeave(self, employeeId, startDate):

        query_str = """SELECT COUNT(h.id) FROM hr_holidays h
                                LEFT JOIN hr_holidays_status hhs ON hhs.id = h.holiday_status_id
                                WHERE h.employee_id = %s AND h.type='remove' 
                                AND h.state IN ('validate1','validate') AND 
                                hhs.unpaid = TRUE AND
                                %s BETWEEN h.date_from::DATE AND h.date_to::DATE"""

        self._cr.execute(query_str, (employeeId, startDate))
        count = self._cr.fetchall()
        if count[0][0] > 0:
            return True
        else:
            return False

    def getHolidaysByUnit(self, unitId, requested_date):
        holidays_query = """select t1.id,t1.date from hr_holidays_public_line as t1
                            join hr_holidays_public as t2 on t2.id=t1.public_type_id
                            join public_holiday_operating_unit_rel as t3 on t3.public_holiday_id=t2.id
                            join date_range as t4 on t4.id=t2.year_id
                            where t3.operating_unit_id=%s and %s between t4.date_start and t4.date_end"""
        # key date value id from
        self._cr.execute(holidays_query, (unitId,requested_date))
        holidaysLines = self._cr.fetchall()
        holidaysMap={}
        for i, line in enumerate(holidaysLines):
            holidaysMap[line[1]] = line[0]

        return holidaysMap

    def getHolidaysByUnitDateRange(self, unitId, from_date, to_date):
        holidays_query = """SELECT t1.id,t1.date FROM hr_holidays_public_line AS t1
                            JOIN hr_holidays_public AS t2 ON t2.id=t1.public_type_id
                            JOIN public_holiday_operating_unit_rel AS t3 ON t3.public_holiday_id=t2.id
                            WHERE t3.operating_unit_id=%s AND t1.date BETWEEN
                                  DATE(%s) and DATE(%s)"""

        self._cr.execute(holidays_query, (unitId, from_date, to_date))
        holidaysLines = self._cr.fetchall()
        holidaysMap = {}
        for i, line in enumerate(holidaysLines):
            holidaysMap[line[1]] = line[0]

        return holidaysMap

    def getCompensatoryLeaveEmpByHolidayLineId(self, lineId):
        holidays_query = """select t1.employee_id from hr_exception_compensatory_leave as t1
                            join hr_holidays_exception_employee_batch as t2 on t1.rel_exception_leave_id=t2.id
                            where t2.public_holidays_line=%s and t2.state='approved'"""
        self._cr.execute(holidays_query, (lineId,))
        holidaysLines = self._cr.fetchall()
        compensatoryLeaveMap={}
        for i, line in enumerate(holidaysLines):
            compensatoryLeaveMap["employee_id"] = ""

        return compensatoryLeaveMap

    def getOTEmpByHolidayLineId(self, lineId):
        ot_query = """select t1.employee_id from hr_exception_overtime_duty as t1
                            join hr_holidays_exception_employee_batch as t2 on t1.rel_exception_ot_id=t2.id
                            where t2.public_holidays_line=%s and t2.state='approved'"""
        self._cr.execute(ot_query, (lineId,))
        otLines = self._cr.fetchall()
        oTMap={}
        for i, line in enumerate(otLines):
            oTMap["employee_id"] = ""

        return oTMap