from openerp import models, fields
from openerp import api
import datetime
from email import _name
from datetime import timedelta

from late_time import TempLateTime
from late_day import TempLateDay
from attendance_summary_line import TempAttendanceSummaryLine
from absent_day import TempAbsentDay
from weekend_day import TempWeekendDay

class AttendanceProcessor(models.Model):
    _name = 'hr.attendance.summary.temp'

    absentGraceMinutes = 10

    period_query = """SELECT ap.date_start, ap.date_stop
                       FROM hr_attendance_summary ac
                       JOIN account_period ap ON ap.id = ac.period
                       WHERE ac.id = %s LIMIT 1"""

    employee_shift_history_query = """SELECT effective_from, shift_id
                                FROM hr_shifting_history
                                WHERE employee_id = %s AND effective_from BETWEEN %s AND %s
                                ORDER BY effective_from ASC"""

    attendance_query = """SELECT (check_in + interval '6h') AS check_in, (check_out + interval '6h') AS check_out, worked_hours
                            FROM hr_attendance
                          WHERE check_out > %s AND check_in < %s AND employee_id = %s
                          ORDER BY check_in ASC"""

    def get_summary_data(self, employeeId, summaryId):

        ############### Delete Current Records ##########################################
        self.env["hr.attendance.summary.line"].search([('employee_id', '=', employeeId), ('att_summary_id', '=', summaryId)]).unlink()

        dutyTimeMap = {}
        shiftList = []
        startDate = datetime.datetime.now() #Current date
        endDate = datetime.datetime.now() #Current date


        # Get Date from Account Period
        self._cr.execute(self.period_query, (summaryId,))
        accountPeriod = self._cr.fetchall()
        if accountPeriod:
            startDate = self.getDateFromStr(accountPeriod[0][0])
            endDate = self.getDateFromStr(accountPeriod[0][1])

        day = datetime.timedelta(days=1)

        preStartDate = startDate - day
        postEndDate = endDate + day

        # Getting Shift Id for an employee
        self._cr.execute(self.employee_shift_history_query, (employeeId, preStartDate, postEndDate))
        calendarList = self._cr.fetchall()
        if not calendarList:
            return

        shiftList = self.getShiftList(calendarList, postEndDate)
        dutyTimeMap = self.buildDutyTime(preStartDate, postEndDate, shiftList)
        self.printDutyTime(preStartDate, postEndDate, dutyTimeMap)

        # Getting Attendance for an employee
        attendance_data = self.GetAttendanceData(dutyTimeMap, employeeId, postEndDate, preStartDate)

        attSummaryLine = TempAttendanceSummaryLine()

        currDate = startDate
        while currDate <= endDate:
            # Check this date is week end or not. If it is empty, then means this day is weekend
            currentDaydutyTime = dutyTimeMap.get(self.getStrFromDate(currDate))
            if currentDaydutyTime:
                attendanceDayList = []
                previousDayDutyTime = self.getPreviousDutyTime(currDate - day, dutyTimeMap)
                nextDayDutyTime = self.getNextDutyTime(currDate + day, dutyTimeMap)
                temp_attendance_data = list(attendance_data)
                for i, attendance in enumerate(attendance_data):
                    if previousDayDutyTime.endActualDutyTime < self.getDateTimeFromStr(
                            attendance[0]) < currentDaydutyTime.endActualDutyTime and \
                                            currentDaydutyTime.startDutyTime < self.getDateTimeFromStr(
                                        attendance[1]) < nextDayDutyTime.startDutyTime:
                        duration = (self.getDateTimeFromStr(attendance[1]) - self.getDateTimeFromStr(attendance[0])).total_seconds() / 60 / 60
                        attendanceDayList.append(TempLateTime(attendance[0], attendance[1], duration))
                        temp_attendance_data.remove(attendance)
                    # If attendance data is greater then 48 hours from current date (startDate) then call break.
                    # Means rest of the attendance date are not illegible for current date. Break condition apply for better optimization
                    elif (self.getDateTimeFromStr(attendance[0]) - currDate).total_seconds() / 60 / 60 > 48:
                        break
                attendance_data = temp_attendance_data
                if attendanceDayList:
                    totalPresentTime = 0
                    # Collect date wise in out data
                    for i, attendanceDay in enumerate(attendanceDayList):
                        totalPresentTime = self.getDayWorkingMinutes(attendanceDay, currentDaydutyTime, totalPresentTime)

                    print(">>>>", currDate, ">>Working Hour<<", totalPresentTime / 60, "List:", len(attendanceDayList))
                    scheduleTime = currentDaydutyTime.dutyMinutes + currentDaydutyTime.otDutyMinutes
                    absentTime = scheduleTime - totalPresentTime

                    if absentTime >= scheduleTime/2:
                        # Before set as absent, check this day is holiday or personal leave
                        if self.checkOnHolidays(currDate) is True:
                            attSummaryLine.holidays_days = attSummaryLine.holidays_days + 1
                            attSummaryLine = self.buildAttendanceDetails(attSummaryLine, currentDaydutyTime)
                        elif self.checkOnPersonalLeave(employeeId, currDate) is True:
                            attSummaryLine.leave_days = attSummaryLine.leave_days + 1
                            attSummaryLine = self.buildAttendanceDetails(attSummaryLine, currentDaydutyTime)
                        else:
                            # @Todo- Check Short Leave. If not approve short leave then absent
                            attSummaryLine = self.buildAbsentDetails(attSummaryLine, currDate, currentDaydutyTime)

                    elif absentTime > 20: # Default gress 20 minutes gress time

                        # Before set as late, check this day is holiday or personal leave
                        if self.checkOnHolidays(currDate) is True:
                            attSummaryLine.holidays_days = attSummaryLine.holidays_days + 1
                            attSummaryLine = self.buildAttendanceDetails(attSummaryLine, currentDaydutyTime)
                        elif self.checkOnPersonalLeave(employeeId, currDate) is True:
                            attSummaryLine.leave_days = attSummaryLine.leave_days + 1
                            attSummaryLine = self.buildAttendanceDetails(attSummaryLine, currentDaydutyTime)
                        else:
                            attSummaryLine = self.buildLateDetails(attSummaryLine, currentDaydutyTime, currDate, absentTime, totalPresentTime, attendanceDayList)

                    else:
                        attSummaryLine.present_days = attSummaryLine.present_days + 1
                        attSummaryLine = self.buildAttendanceDetails(attSummaryLine, currentDaydutyTime)

                else:
                    if self.checkOnHolidays(currDate) is True:
                        attSummaryLine.holidays_days = attSummaryLine.holidays_days + 1
                        attSummaryLine = self.buildAttendanceDetails(attSummaryLine, currentDaydutyTime)
                    elif self.checkOnPersonalLeave(employeeId, currDate) is True:
                        attSummaryLine.leave_days = attSummaryLine.leave_days + 1
                        attSummaryLine = self.buildAttendanceDetails(attSummaryLine, currentDaydutyTime)
                    else:
                        attSummaryLine = self.buildAbsentDetails(attSummaryLine, currDate, currentDaydutyTime)
            else:
                attSummaryLine = self.buildWeekEnd(attSummaryLine, currDate)

            currDate = currDate + day

        noOfDays = (endDate - startDate).days + 1
        self.saveAttSummary(employeeId, summaryId, noOfDays, attSummaryLine)



    def process(self, employeeIds, summaryId):
        for empId in employeeIds:
            self.get_summary_data(empId, summaryId)


    ############################# Utility Methods ####################################################################

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
                            "isIncludedOt", ot_hour_from, ot_hour_to
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
                                                         shiftLine[4], shiftLine[5])
        return shiftLinesMap

    def buildDutyTime(self, preStartDate, postEndDate, shiftList):
        dutyTimeMap = {}
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

                        dutyTimeMap[preStartDate.strftime('%Y.%m.%d')] = DutyTime(startDutyTime, endDutyTime, shiftObj.isot, otStartDutyTime, otEndDutyTime)
                        break
            preStartDate = preStartDate + day
        return dutyTimeMap

    def printDutyTime(self, preStartDate, postEndDate, dutyTimeMap):
        day = datetime.timedelta(days=1)
        print ">>>>>>>>>>>>>>>>>> For Test Data >>>>>>>>>>>>>>>>>"
        while preStartDate <= postEndDate:
            dt = dutyTimeMap.get(preStartDate.strftime('%Y.%m.%d'))
            if dt:
                print (
                preStartDate.strftime('%Y.%m.%d'), "Start:", dt.startDutyTime.strftime('%Y.%m.%d-%H:%M:%S'), "End:",
                dt.endDutyTime.strftime('%Y.%m.%d-%H:%M:%S'), "Diff:", dt.dutyMinutes / 60)
            preStartDate = preStartDate + day
        print ">>>>>>>>>>>>>>>>>> End For Test Data >>>>>>>>>>>>>>>>>"

    # Get previous duty time. If previous duty time is null that means this day was weekend.
    # Then set a default time at previous day
    def getPreviousDutyTime(self, date, dutyTimeMap):
        previousDayDutyTime = dutyTimeMap.get(self.getStrFromDate(date))
        if previousDayDutyTime:
            return previousDayDutyTime
        else:
            previousDayDutyTime = DutyTime(date + timedelta(hours=22), date + timedelta(hours=23), False, 0, 0)
            return previousDayDutyTime

    # Get next duty time. If previous duty time is null that means this day was weekend.
    # Then set a default time at previous day
    def getNextDutyTime(self, date, dutyTimeMap):
        nextDutyTime = dutyTimeMap.get(self.getStrFromDate(date))
        if nextDutyTime:
            return nextDutyTime
        else:
            nextDutyTime = DutyTime(date + timedelta(hours=23.9), date + timedelta(hours=23.95), False, 0, 0)
            return nextDutyTime

    def checkOnPersonalLeave(self, employeeId, startDate):

        query_str = """SELECT COUNT(id) FROM hr_holidays
                           WHERE employee_id = %s AND type='remove' AND state = 'validate' AND
                           %s BETWEEN date_from::DATE AND date_to::DATE"""

        self._cr.execute(query_str, (employeeId, startDate.date()))
        count = self._cr.fetchall()
        if count[0][0] > 0:
            return True
        else:
            return False

    def checkOnHolidays(self, startDate):

        query_str = """SELECT COUNT(id) FROM hr_holidays_public_line
                       WHERE date = %s AND status = true"""

        self._cr.execute(query_str, (startDate.date(),))
        count = self._cr.fetchall()
        if count[0][0] > 0:
            return True
        else:
            return False


    def buildAttendanceDetails(self, attSummaryLine, currentDayDutyTime):
        if currentDayDutyTime.isot is True:
            attSummaryLine.schedule_ot_hrs = attSummaryLine.schedule_ot_hrs + currentDayDutyTime.otDutyMinutes / 60
        return attSummaryLine

    def buildLateDetails(self, attSummaryLine, currentDayDutyTime, startDate, absentTime, totalPresentTime, attendanceDayList):

        attSummaryLine = self.buildAttendanceDetails(attSummaryLine, currentDayDutyTime)

        attSummaryLine.late_hrs = attSummaryLine.late_hrs + absentTime / 60
        attSummaryLine.late_days.append(TempLateDay(startDate, currentDayDutyTime.startDutyTime,
                                                          currentDayDutyTime.endDutyTime,
                                                          currentDayDutyTime.otStartDutyTime,
                                                          currentDayDutyTime.otEndDutyTime,
                                                          (currentDayDutyTime.dutyMinutes + currentDayDutyTime.otDutyMinutes)/ 60,
                                                         totalPresentTime/60, attendanceDayList))
        return attSummaryLine

    def buildAbsentDetails(self, attSummaryLine, startDate, currentDayDutyTime):
        attSummaryLine = self.buildAttendanceDetails(attSummaryLine, currentDayDutyTime)
        attSummaryLine.absent_days.append(TempAbsentDay(startDate))
        return attSummaryLine

    def buildWeekEnd(self, attSummaryLine, startDate):
        attSummaryLine.weekend_days.append(TempWeekendDay(startDate))
        return attSummaryLine

    def GetAttendanceData(self, dutyTimeMap, employeeId, postEndDate, preStartDate):
        dutyTime_s = dutyTimeMap.get(self.getStrFromDate(preStartDate))
        if dutyTime_s:
            att_time_start = dutyTime_s.endDutyTime
        else:
            att_time_start = preStartDate + timedelta(hours=23)
        att_time_end = dutyTimeMap.get(self.getStrFromDate(postEndDate)).startDutyTime
        self._cr.execute(self.attendance_query, (att_time_start, att_time_end, employeeId))
        attendance_data = self._cr.fetchall()



        #######################################################################################################

        #attendance_data5 = self.env["hr.attendance"].search([('employee_id', '=', employeeId)], order='check_in ASC')


        return attendance_data


    def getDayWorkingMinutes(self, attendanceDay, currentDaydutyTime, totalMinute):
        ch_in = self.getDateTimeFromStr(attendanceDay.check_in)
        ch_out = self.getDateTimeFromStr(attendanceDay.check_out)
        if ch_in < currentDaydutyTime.startDutyTime:
            ch_in = currentDaydutyTime.startDutyTime
        if ch_out > currentDaydutyTime.endActualDutyTime:
            ch_out = currentDaydutyTime.endActualDutyTime
        totalMinute = totalMinute + (ch_out - ch_in).total_seconds() / 60
        return totalMinute

    def saveAttSummary(self, employeeId, summaryId, noOfDays, attSummaryLine):

        summary_line_pool = self.env['hr.attendance.summary.line']
        weekend_pool = self.env['hr.attendance.weekend.day']
        absent_pool = self.env['hr.attendance.absent.day']
        late_day_pool = self.env['hr.attendance.late.day']
        late_time_pool = self.env['hr.attendance.late.time']

        ############## Save Summary Lines ######################
        salaryDays = noOfDays - len(attSummaryLine.absent_days)
        calOtHours = 0
        if attSummaryLine.schedule_ot_hrs > attSummaryLine.late_hrs:
            calOtHours = attSummaryLine.schedule_ot_hrs - attSummaryLine.late_hrs


        vals = {'employee_id':      employeeId,
                'att_summary_id':   summaryId,
                'salary_days':      salaryDays,
                'present_days':     attSummaryLine.present_days,
                'holidays_days':    attSummaryLine.holidays_days,
                'leave_days':       attSummaryLine.leave_days,
                'late_hrs':         attSummaryLine.late_hrs,
                'schedule_ot_hrs':  attSummaryLine.schedule_ot_hrs,
                'cal_ot_hrs':       calOtHours ,

                }
        res = summary_line_pool.create(vals)
        att_summary_line_id = res.id

        ############## Save Weekend Days ######################
        for i, weekend in enumerate(attSummaryLine.weekend_days):
            weekendVals = {'date': weekend.date, 'att_summary_line_id': att_summary_line_id}
            res = weekend_pool.create(weekendVals)

        ############## Save Absent Days ######################
        for i, absent in enumerate(attSummaryLine.absent_days):
            absentVals = {'date': absent.date, 'att_summary_line_id': att_summary_line_id}
            res = absent_pool.create(absentVals)

        ############## Save Late Days ######################
        for i, lateDay in enumerate(attSummaryLine.late_days):

            lateDayVals = {'date': lateDay.date,
                           'schedule_time_start': self.convertDateTime(lateDay.schedule_time_start),
                           'schedule_time_end': self.convertDateTime(lateDay.schedule_time_end),
                           'ot_time_start': self.convertDateTime(lateDay.ot_time_start),
                           'ot_time_end': self.convertDateTime(lateDay.ot_time_end),
                           'schedule_working_hours': lateDay.schedule_working_hours,
                           'working_hours': lateDay.working_hours,
                           'att_summary_line_id': att_summary_line_id
                     }
            res = late_day_pool.create(lateDayVals)
            late_day_id = res.id

            ############## Save Late Times ######################
            for i, time in enumerate(lateDay.attendance_day_list):
                timeVals = {'check_in': self.convertStrDateTime(time.check_in),
                            'check_out': self.convertStrDateTime(time.check_out),
                            'duration': time.duration,
                            'late_day_id': late_day_id
                         }
                res = late_time_pool.create(timeVals)



    def getStrFromDate(self, date):
        return date.strftime('%Y.%m.%d')

    def getDateTimeFromStr(self, dateStr):
        return datetime.datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S")

    def convertDateTime(self, dateStr):
        return dateStr + timedelta(hours=-6)

    def convertStrDateTime(self, dateStr):
        return self.getDateTimeFromStr(dateStr) + timedelta(hours=-6)

    def getDateFromStr(self, dateStr):
        if dateStr:
            return datetime.datetime.strptime(dateStr, "%Y-%m-%d")
        else:
            return datetime.datetime.now()

    ############################# Utility Methods ####################################################################

class Shift(object):
    def __init__(self, effectiveDtStr=None, effectiveDtEnd=None, shiftId=None, shiftLines=None):
        self.effectiveDtStr = effectiveDtStr
        self.effectiveDtEnd = effectiveDtEnd
        self.shiftId = shiftId
        self.shiftLines = shiftLines


class ShiftLine(object):
    def __init__(self, weekDay=None, startTime=None, endTime=None, isot=None, otStartTime=None, otEndTime=None):
        self.weekDay = int(weekDay)
        self.startTime = startTime
        self.endTime = endTime
        self.isot = isot
        self.otStartTime = otStartTime
        self.otEndTime = otEndTime


class DutyTime(object):
    def __init__(self, startDutyTime=None, endDutyTime=None, isot=None, otStartDutyTime=None, otEndDutyTime=None):
        self.startDutyTime = startDutyTime
        self.endDutyTime = endDutyTime
        self.endActualDutyTime = endDutyTime
        self.isot = isot
        self.otStartDutyTime = otStartDutyTime
        self.otEndDutyTime = otEndDutyTime
        if isot is True:
            self.dutyMinutes = (endDutyTime - startDutyTime).total_seconds() / 60
            self.otDutyMinutes = (otEndDutyTime - otStartDutyTime).total_seconds() / 60
            self.endActualDutyTime = otEndDutyTime
        else:
            self.dutyMinutes = (endDutyTime - startDutyTime).total_seconds() / 60
            self.otDutyMinutes = 0