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

    salary_deduction_late_day = 3

    period_query = """SELECT ap.date_start, ap.date_stop
                       FROM hr_attendance_summary ac
                       JOIN account_period ap ON ap.id = ac.period
                       WHERE ac.id = %s LIMIT 1"""


    attendance_query = """SELECT (check_in + interval '6h') AS check_in, (check_out + interval '6h') AS check_out, worked_hours
                            FROM hr_attendance
                          WHERE check_out > %s AND check_in < %s AND employee_id = %s AND has_error = False
                          ORDER BY check_in ASC"""



    def get_summary_data(self, employeeId, summaryId, graceTime, operating_unit_id, att_utility_pool):

        ############### Delete Current Records ##########################################
        self.env["hr.attendance.summary.line"].search([('employee_id', '=', employeeId), ('att_summary_id', '=', summaryId)]).unlink()

        hr_employee_pool = self.env['hr.employee']
        employee = hr_employee_pool.search([('id', '=', employeeId)])

        startDate = datetime.datetime.now() #Current date
        endDate = datetime.datetime.now() #Current date
        day = datetime.timedelta(days=1)

        # Get Date from Account Period
        self._cr.execute(self.period_query, (summaryId,))
        accountPeriod = self._cr.fetchall()
        if accountPeriod:
            startDate = self.getDateFromStr(accountPeriod[0][0])
            endDate = self.getDateFromStr(accountPeriod[0][1])

        preStartDate = startDate - day
        postEndDate = endDate + day

        dutyTimeMap = att_utility_pool.getDutyTimeByEmployeeId(employeeId, preStartDate, postEndDate)
        alterTimeMap = att_utility_pool.buildAlterDutyTime(startDate, endDate, employeeId)

        holidayMap = att_utility_pool.getHolidaysByUnitDateRange(operating_unit_id, startDate, endDate)

        # Getting Attendance for an employee
        attendance_data = self.getAttendanceData(dutyTimeMap, employeeId, postEndDate, preStartDate)

        attSummaryLine = TempAttendanceSummaryLine()

        if len(dutyTimeMap) != 0: # Check Rostering data are centered or not
            currDate = startDate
            while currDate <= endDate:

                if alterTimeMap.get(self.getStrFromDate(currDate)): # Check this date is alter date
                    alterDayDutyTime = alterTimeMap.get(self.getStrFromDate(currDate))
                    attendanceDayList = att_utility_pool.getAttendanceListByAlterDay(alterDayDutyTime, day, dutyTimeMap, employeeId)
                    attSummaryLine = self.makeDecision(attSummaryLine, attendanceDayList, currDate, alterDayDutyTime, employee, graceTime, holidayMap, att_utility_pool)

                elif dutyTimeMap.get(self.getStrFromDate(currDate)): # Check this date is week end or not. If it is empty, then means this day is weekend
                    currentDaydutyTime = dutyTimeMap.get(self.getStrFromDate(currDate))
                    attendanceDayList = att_utility_pool.getAttendanceListByDay(attendance_data, currDate, currentDaydutyTime, day, dutyTimeMap)
                    attSummaryLine = self.makeDecision(attSummaryLine, attendanceDayList, currDate, currentDaydutyTime, employee, graceTime, holidayMap, att_utility_pool)
                else:
                    attSummaryLine = self.buildWeekEnd(attSummaryLine, currDate)

                currDate = currDate + day
        else:
            attSummaryLine.is_entered_rostering = 0

        noOfDays = (endDate - startDate).days + 1
        # @Todo-Bappy Get extra OT
        query = """SELECT total_hours FROM hr_ot_requisition WHERE from_datetime 
                    BETWEEN %s AND %s AND state = 'approved' AND employee_id = %s"""
        self._cr.execute(query, tuple([startDate, endDate, employeeId]))
        get_query_extra_ot = self._cr.fetchone()
        if get_query_extra_ot:
            get_extra_ot = get_query_extra_ot[0]
        else:
            get_extra_ot = 0

        self.saveAttSummary(employeeId, summaryId, noOfDays, attSummaryLine,get_extra_ot)

    def makeDecision(self, attSummaryLine, attendanceDayList, currDate, currentDaydutyTime, employee, graceTime, holidayMap, att_utility_pool):

        employeeId = employee.id


        # Check for Holiday
        if self.checkOnHolidays(currDate, holidayMap, employee, att_utility_pool) is True:
            attSummaryLine.holidays_days = attSummaryLine.holidays_days + 1
            return attSummaryLine

        # Check for Personal Leave
        if att_utility_pool.checkOnPersonalLeave(employeeId, currDate) is True:
            attSummaryLine.leave_days = attSummaryLine.leave_days + 1
            return attSummaryLine

        # Check for Un-monitor Employee. Like as: CXO,MD,Driver
        if employee.is_monitor_attendance == False:
            attSummaryLine.present_days = attSummaryLine.present_days + 1
            attSummaryLine = self.calculateScheduleOtHrs(attSummaryLine, currentDaydutyTime)
            return attSummaryLine


        totalPresentTime = 0
        off_duty = 0

        if attendanceDayList:

            attSummaryLine.present_days = attSummaryLine.present_days + 1

            scheduleTime = currentDaydutyTime.dutyMinutes + currentDaydutyTime.otDutyMinutes

            if employee.is_executive == True:
                totalPresentTime = self.getDayWorkingMinutesForManagement(attendanceDayList, currentDaydutyTime)
                off_duty = scheduleTime - totalPresentTime
                if off_duty < 0:
                    off_duty = 0
            else:
                #Collect date wise in out data
                for i, attendanceDay in enumerate(attendanceDayList):
                    totalPresentTime = self.getDayWorkingMinutesForNonManagement(attendanceDay, currentDaydutyTime, totalPresentTime)

                off_duty = scheduleTime - (totalPresentTime + currentDaydutyTime.graceTime)
                if off_duty < 0:
                    off_duty = 0

            if off_duty > 0:
                attSummaryLine.late_hrs = attSummaryLine.late_hrs + off_duty / 60

            # Check is late or not by checking day first in time.
            # We collect first row because attendance are shorted by check_in time ASC
            isLate = att_utility_pool.isLateByInTime(self.getDateTimeFromStr(attendanceDayList[0].check_in), currentDaydutyTime, graceTime)

            if isLate == True:
                attSummaryLine = self.buildLateDetails(attSummaryLine, currentDaydutyTime, currDate,totalPresentTime, attendanceDayList)
               # if att_utility_pool.checkShortLeave(self.convertDateTime(currentDaydutyTime.startDutyTime)) is False:
               #     attSummaryLine = self.buildLateDetails(attSummaryLine, currentDaydutyTime, currDate, totalPresentTime, attendanceDayList)
               # else:
               #     # Present without late, Because at this time employee was in short leave
               #     attSummaryLine = self.calculateScheduleOtHrs(attSummaryLine, currentDaydutyTime)
            else:
                # Present without late
                attSummaryLine = self.calculateScheduleOtHrs(attSummaryLine, currentDaydutyTime)
        else:
            attSummaryLine = self.buildAbsentDetails(attSummaryLine, currentDaydutyTime, currDate, totalPresentTime, attendanceDayList)

        return attSummaryLine

    def process(self, employeeIds, summaryId, operating_unit_id):
        att_utility_pool = self.env['attendance.utility']
        graceTime = att_utility_pool.getGraceTime(datetime.datetime.now())

        # @Todo-Bappy Get Joining Date
        # Get Date from Account Period
        # self._cr.execute(self.period_query, (summaryId,))
        # accountPeriod = self._cr.fetchall()
        # if accountPeriod:
        #     startDate = self.getDateFromStr(accountPeriod[0][0])
        #     endDate = self.getDateFromStr(accountPeriod[0][1])

        #################################################################


        for empId in employeeIds:
            self.get_summary_data(empId, summaryId, graceTime, operating_unit_id, att_utility_pool)


    ############################# Utility Methods ####################################################################

    def checkOnHolidays(self, startDate, holidayMap, employee, att_utility_pool):

        compensatoryLeaveMap = {}
        oTMap = {}
        todayIsHoliday = False
        start_date = att_utility_pool.getStrFromDate2(startDate)
        if holidayMap.get(start_date):
            lineId = holidayMap.get(start_date)
            todayIsHoliday = True
            compensatoryLeaveMap = att_utility_pool.getCompensatoryLeaveEmpByHolidayLineId(lineId)
            oTMap = att_utility_pool.getOTEmpByHolidayLineId(lineId)

        if employee.is_monitor_attendance == False & todayIsHoliday == True:
            return True
        else:
            return att_utility_pool.checkOnHolidays(employee.id, todayIsHoliday, compensatoryLeaveMap, oTMap)




    def calculateScheduleOtHrs(self, attSummaryLine, currentDayDutyTime):

        if currentDayDutyTime.isot is True:
            attSummaryLine.schedule_ot_hrs = attSummaryLine.schedule_ot_hrs + currentDayDutyTime.otDutyMinutes / 60
        return attSummaryLine

    def buildLateDetails(self, attSummaryLine, currentDayDutyTime, startDate, totalPresentTime, attendanceDayList):

        attSummaryLine = self.calculateScheduleOtHrs(attSummaryLine, currentDayDutyTime)

        attSummaryLine.late_days.append(TempLateDay(startDate, currentDayDutyTime.startDutyTime,
                                                          currentDayDutyTime.endDutyTime,
                                                          currentDayDutyTime.otStartDutyTime,
                                                          currentDayDutyTime.otEndDutyTime,
                                                          (currentDayDutyTime.dutyMinutes + currentDayDutyTime.otDutyMinutes)/ 60,
                                                         totalPresentTime/60, attendanceDayList))
        return attSummaryLine

    def buildAbsentDetails(self, attSummaryLine, currentDayDutyTime, startDate, totalPresentTime, attendanceDayList):

        attSummaryLine.absent_days.append(TempAbsentDay(startDate, currentDayDutyTime.startDutyTime,
                                                    currentDayDutyTime.endDutyTime,
                                                    currentDayDutyTime.otStartDutyTime,
                                                    currentDayDutyTime.otEndDutyTime,
                                                    (
                                                    currentDayDutyTime.dutyMinutes + currentDayDutyTime.otDutyMinutes) / 60,
                                                    totalPresentTime / 60, attendanceDayList))
        return attSummaryLine

    def buildWeekEnd(self, attSummaryLine, startDate):
        attSummaryLine.weekend_days.append(TempWeekendDay(startDate))
        return attSummaryLine

    def getAttendanceData(self, dutyTimeMap, employeeId, postEndDate, preStartDate):
        dutyTime_s = dutyTimeMap.get(self.getStrFromDate(preStartDate))
        if dutyTime_s:
            att_time_start = dutyTime_s.endDutyTime
        else:
            att_time_start = preStartDate + timedelta(hours=23)

        dutyTime_e = dutyTimeMap.get(self.getStrFromDate(postEndDate))
        if dutyTime_e:
            att_time_end = dutyTime_e.startDutyTime
        else:
            att_time_end = postEndDate + timedelta(hours=1)
        # att_time_end = dutyTimeMap.get(self.getStrFromDate(postEndDate)).startDutyTime
        self._cr.execute(self.attendance_query, (att_time_start, att_time_end, employeeId))
        attendance_data = self._cr.fetchall()

        return attendance_data

    def getDayWorkingMinutesForManagement(self, attendanceDayList, currentDaydutyTime):

        first_check_in = self.getDateTimeFromStr(attendanceDayList[0].check_in)
        last_check_out = self.getDateTimeFromStr(attendanceDayList[len(attendanceDayList) - 1].check_out)
        if currentDaydutyTime.startDutyTime > first_check_in:
            first_check_in = currentDaydutyTime.startDutyTime

        totalMinute = (last_check_out - first_check_in).total_seconds() / 60
        return totalMinute

    def getDayWorkingMinutesForNonManagement(self, attendanceDay, currentDaydutyTime, totalMinute):
        ch_in = self.getDateTimeFromStr(attendanceDay.check_in)
        ch_out = self.getDateTimeFromStr(attendanceDay.check_out)
        if ch_in < currentDaydutyTime.startDutyTime:
            ch_in = currentDaydutyTime.startDutyTime
        if ch_out > currentDaydutyTime.endActualDutyTime:
            ch_out = currentDaydutyTime.endActualDutyTime
        totalMinute = totalMinute + (ch_out - ch_in).total_seconds() / 60
        return totalMinute




    def saveAttSummary(self, employeeId, summaryId, noOfDays, attSummaryLine,get_extra_ot):

        summary_line_pool = self.env['hr.attendance.summary.line']
        weekend_pool = self.env['hr.attendance.weekend.day']
        absent_pool = self.env['hr.attendance.absent.day']
        absent_time_pool = self.env['hr.attendance.absent.time']
        late_day_pool = self.env['hr.attendance.late.day']
        late_time_pool = self.env['hr.attendance.late.time']

        ############## Save Summary Lines ######################
        salaryDays = noOfDays - len(attSummaryLine.absent_days)
        calOtHours = attSummaryLine.schedule_ot_hrs + get_extra_ot
        #@Todo-Bappy Add extra OT with calOtHours
        if attSummaryLine.schedule_ot_hrs > attSummaryLine.late_hrs:
            calOtHours = attSummaryLine.schedule_ot_hrs - attSummaryLine.late_hrs


        vals = {'employee_id':      employeeId,
                'att_summary_id':   summaryId,
                'salary_days':      salaryDays,
                'present_days':     attSummaryLine.present_days,
                'holidays_days':    attSummaryLine.holidays_days,
                'leave_days':       attSummaryLine.leave_days,
                'deduction_days':   int(len(attSummaryLine.late_days)/self.salary_deduction_late_day),
                'late_hrs':         attSummaryLine.late_hrs,
                'schedule_ot_hrs':  attSummaryLine.schedule_ot_hrs,
                'cal_ot_hrs':       calOtHours,
                'extra_ot':         get_extra_ot,
                'is_entered_rostering': attSummaryLine.is_entered_rostering

                }
        res = summary_line_pool.create(vals)
        att_summary_line_id = res.id

        ############## Save Weekend Days ######################
        for i, weekend in enumerate(attSummaryLine.weekend_days):
            weekendVals = {'date': weekend.date, 'att_summary_line_id': att_summary_line_id}
            res = weekend_pool.create(weekendVals)

        ############## Save Absent Days ######################
        for i, absent in enumerate(attSummaryLine.absent_days):
            absentVals = {'date': absent.date,
                           'schedule_time_start': self.convertDateTime(absent.schedule_time_start),
                           'schedule_time_end': self.convertDateTime(absent.schedule_time_end),
                           'ot_time_start': self.convertDateTime(absent.ot_time_start),
                           'ot_time_end': self.convertDateTime(absent.ot_time_end),
                           'schedule_working_hours': absent.schedule_working_hours,
                           'working_hours': absent.working_hours,
                           'att_summary_line_id': att_summary_line_id
                           }
            res = absent_pool.create(absentVals)
            absent_day_id = res.id

            ############## Save Late Times ######################
            for i, time in enumerate(absent.attendance_day_list):
                absentTimeVals = {'check_in': self.convertStrDateTime(time.check_in),
                            'check_out': self.convertStrDateTime(time.check_out),
                            'duration': time.duration,
                            'absent_day_id': absent_day_id
                            }
                res = absent_time_pool.create(absentTimeVals)




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
        if dateStr:
            return datetime.datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
        else:
            return None

    def convertDateTime(self, dateStr):
        if dateStr:
            return dateStr + timedelta(hours=-6)

    def convertStrDateTime(self, dateStr):
        if dateStr:
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
    def __init__(self, weekDay=None, startTime=None, endTime=None, isot=None, otStartTime=None, otEndTime=None, graceTime=None):
        self.weekDay = int(weekDay)
        self.startTime = startTime
        self.endTime = endTime
        self.isot = isot
        self.otStartTime = otStartTime
        self.otEndTime = otEndTime
        self.graceTime = graceTime


class DutyTime(object):
    def __init__(self, startDutyTime=None, endDutyTime=None, isot=None, otStartDutyTime=None, otEndDutyTime=None, graceTime=None):
        self.startDutyTime = startDutyTime
        self.endDutyTime = endDutyTime
        self.endActualDutyTime = endDutyTime
        self.isot = isot
        self.otStartDutyTime = otStartDutyTime
        self.otEndDutyTime = otEndDutyTime
        self.graceTime = graceTime * 60
        if isot is True:
            self.dutyMinutes = (endDutyTime - startDutyTime).total_seconds() / 60
            self.otDutyMinutes = (otEndDutyTime - otStartDutyTime).total_seconds() / 60
            self.endActualDutyTime = otEndDutyTime
        else:
            self.dutyMinutes = (endDutyTime - startDutyTime).total_seconds() / 60
            self.otDutyMinutes = 0