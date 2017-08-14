from odoo import api, fields, models,tools
import datetime
from datetime import timedelta
from utility_class import Shift,ShiftLine,DutyTime,TempLateTime,Employee


class AttendanceUtility(models.Model):
    _name = "attendance.utility"
    _auto = False

    employee_shift_history_query = """SELECT effective_from, shift_id
                                    FROM hr_shifting_history
                                    WHERE employee_id = %s AND effective_from BETWEEN %s AND %s
                                    ORDER BY effective_from ASC"""

    daily_attendance_query = """SELECT (check_in + interval '6h') AS check_in, (check_out + interval '6h') AS check_out, worked_hours
                                        FROM hr_attendance
                                      WHERE employee_id = %s AND check_in between %s and %s AND (check_out IS NULL OR check_out > %s)
                                      ORDER BY check_in ASC LIMIT 1"""

    alter_attendance_query = """SELECT (check_in + interval '6h') AS check_in, (check_out + interval '6h') AS check_out, worked_hours
                                    FROM hr_attendance
                                  WHERE (check_in BETWEEN %s AND %s) AND (check_out BETWEEN %s AND %s) AND employee_id = %s
                                  ORDER BY check_in ASC"""


    def getDutyTimeByEmployeeId(self, employeeId, preStartDate, postEndDate):
        # Getting Shift Ids for an employee
        self._cr.execute(self.employee_shift_history_query, (employeeId, preStartDate, postEndDate))
        calendarList = self._cr.fetchall()
        shiftList = self.getShiftList(calendarList, postEndDate)
        dutyTimeMap = self.buildDutyTime(preStartDate, postEndDate, shiftList)
        self.printDutyTime(preStartDate, postEndDate, dutyTimeMap)
        return dutyTimeMap


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
        previousDayDutyTime = self.getPreviousDutyTime(alterDayDutyTime.startDutyTime - day, dutyTimeMap)
        nextDayDutyTime = self.getNextDutyTime(alterDayDutyTime.startDutyTime + day, dutyTimeMap)

        self._cr.execute(self.alter_attendance_query, (self.convertDateTime(previousDayDutyTime.endActualDutyTime),
                                                       self.convertDateTime(alterDayDutyTime.endActualDutyTime),
                                                       self.convertDateTime(alterDayDutyTime.startDutyTime),
                                                       self.convertDateTime(nextDayDutyTime.startDutyTime),
                                                       employeeId))
        attendance_line = self._cr.fetchall()

        for i, attendance in enumerate(attendance_line):
                duration = (self.getDateTimeFromStr(attendance[1]) - self.getDateTimeFromStr(attendance[0])).total_seconds() / 60 / 60
                attendanceDayList.append(TempLateTime(attendance[0], attendance[1], duration))
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
                            ORDER BY dayofweek ASC"""

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

    def makeDecisionForADays(self, att_summary, attendanceDay, currDate, currentDaydutyTime, employee):

        employeeId = employee.id

        if attendanceDay:

            ##### Check is late or not by checking day first in time. We collect first row
            # because attendance are shorted by check_in time ASC
            isLate = self.isLateByInTime(attendanceDay, currentDaydutyTime)

            if isLate == True:  # Check Absent OR Late
                # Check this day is holiday or personal leave
                if self.checkOnHolidays(currDate) is True:
                    att_summary["holidays"] =  att_summary["holidays"] + 1
                elif self.checkOnPersonalLeave(employeeId, currDate) is True:
                    att_summary["leave"].append(Employee(employee))
                elif 1 == 1:
                    # @Todo- Check Short Leave
                    att_summary["short_leave"].append(Employee(employee))
                elif isLate == True:
                    att_summary["late"].append(Employee(employee))

            else:
                att_summary["on_time_present"].append(Employee(employee))

        else:
            if self.checkOnHolidays(currDate) is True:
                att_summary["holidays"].append(Employee(employee))
            elif self.checkOnPersonalLeave(employeeId, currDate) is True:
                att_summary["leave"].append(Employee(employee))
            elif 1==1:
                # @Todo- Check Short Leave
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
            previousDayDutyTime = DutyTime(date + timedelta(hours=22), date + timedelta(hours=23), False, 0, 0, 0)
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

    # Utility Methods
    def getDateFromStr(self, dateStr):
        if dateStr:
            return datetime.datetime.strptime(dateStr, "%Y-%m-%d")
        else:
            return datetime.datetime.now()

    def getStrFromDate(self, date):
        return date.strftime('%Y.%m.%d')

    ### Short Leave Check Method

    def checkShortLeave(self,datetime_sl):
        leave_pool=self.env['hr.short.leave'].search([('date_from', '<=', datetime_sl),
                                                 ('date_to', '>=',datetime_sl )])
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
        ##4.01666666667?