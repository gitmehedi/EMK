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

    # salary_deduction_late_day = 3

    period_query = """SELECT dr.date_start, dr.date_end 
                      FROM hr_attendance_summary ac
                      JOIN date_range dr ON dr.id = ac.period
                      JOIN date_range_type dt ON dr.type_id = dt.id
                      WHERE dt.holiday_month = True AND ac.id = %s LIMIT 1"""

    # period_query = """SELECT ap.date_start, ap.date_stop
    #                        FROM hr_attendance_summary ac
    #                        JOIN account_period ap ON ap.id = ac.period
    #                        WHERE ac.id = %s LIMIT 1"""


    # attendance_query = """SELECT (check_in + interval '6h') AS check_in, (check_out + interval '6h') AS check_out, worked_hours
    #                         FROM hr_attendance
    #                       WHERE check_out > %s AND check_in < %s AND employee_id = %s AND has_error = False
    #                       ORDER BY check_in ASC"""


    attendance_query = """SELECT (check_in + interval '6h') AS check_in, 
                                   (check_out + interval '6h') AS check_out, 
                                   worked_hours, 1 AS att_type
                            FROM hr_attendance
                            WHERE employee_id = %s AND check_out > %s AND check_in < %s AND
                                  has_error = False
                            UNION
                            SELECT (check_in + interval '6h') AS check_in, 
                                   (check_out + interval '6h') AS check_out, 
                                   0 AS worked_hours, 2 AS att_type
                            FROM hr_manual_attendance 
                            WHERE employee_id = %s AND state = 'validate' AND sign_type = 'both' AND 
                                  check_out > %s AND check_in < %s
                            UNION
                            SELECT (date_from + interval '6h') AS check_in, 
                                   (date_to + interval '6h') AS check_out, 
                                   0 AS worked_hours, 3 AS att_type      
                            FROM hr_short_leave 
                            WHERE employee_id = %s AND state = 'validate' AND 
                                date_to > %s AND date_from < %s
                            ORDER BY check_in, att_type ASC"""

    getExtraOTQuery = """SELECT 
                            SUM(total_hours)
                       FROM 
                            hr_ot_requisition 
                       WHERE 
                            from_datetime BETWEEN %s AND %s AND 
                            state = 'approved' AND 
                            employee_id = %s"""

    def get_summary_data(self, employeeId, summaryId, graceTime, operating_unit_id, att_utility_pool, empJoiningDateMap):

        ############### Delete Current Records ##########################################
        self.env["hr.attendance.summary.line"].search([('employee_id', '=', employeeId), ('att_summary_id', '=', summaryId)]).unlink()

        hr_employee_pool = self.env['hr.employee']

        employee = hr_employee_pool.search(['&', ('id', '=', employeeId), '|', ('active', '=', True), ('active', '=', False)])
        if employee.initial_employment_date and len(employee.initial_employment_date) > 0:
            initial_employment_date = self.getDateFromStr(employee.initial_employment_date)
        else:
            initial_employment_date = False

        if employee.last_employment_date and len(employee.last_employment_date) > 0:
            last_employment_date = self.getDateFromStr(employee.last_employment_date)
        else:
            last_employment_date = False

        day = datetime.timedelta(days=1)

        # Get Date from Account Period
        accPeriodResult = self.getAccountPeriodDate(summaryId)
        startDate = accPeriodResult.values()[0]
        endDate = accPeriodResult.values()[1]

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
            if initial_employment_date and initial_employment_date > currDate:
                attSummaryLine.nis_days = attSummaryLine.nis_days + (initial_employment_date - currDate).days
                currDate = initial_employment_date

            if last_employment_date and last_employment_date < endDate:
                attSummaryLine.nis_days = attSummaryLine.nis_days + (endDate - last_employment_date).days
                endDate = last_employment_date

            # 'hr.holiday.allowance'
            holidayAlwMap = att_utility_pool.getHolidayAlwByEmployee(employeeId, currDate, endDate)

            while currDate <= endDate:

                # Check for Personal Leave
                if att_utility_pool.checkOnPersonalLeave(employeeId, currDate) is True:
                    attSummaryLine.leave_days = attSummaryLine.leave_days + 1

                # Check for Unpaid Leave
                elif att_utility_pool.checkOnUnpaidLeave(employeeId, currDate) is True:
                    attSummaryLine.unpaid_holidays = attSummaryLine.unpaid_holidays + 1

                elif alterTimeMap.get(self.getStrFromDate(currDate)): # Check this date is alter date
                    alterDayDutyTime = alterTimeMap.get(self.getStrFromDate(currDate))
                    attendanceDayList = att_utility_pool.getAttendanceListByAlterDay(alterDayDutyTime, day, dutyTimeMap, employeeId)
                    altCurrDate = datetime.datetime.strptime(alterDayDutyTime.startDutyTime.strftime('%Y-%m-%d'), '%Y-%m-%d')
                    attSummaryLine = self.makeDecision(attSummaryLine, attendanceDayList, altCurrDate, alterDayDutyTime, employee, graceTime, holidayMap, empJoiningDateMap, att_utility_pool)

                elif holidayAlwMap.get(currDate.strftime('%Y-%m-%d')):
                    currentDaydutyTime = dutyTimeMap.get(self.getStrFromDate(currDate))
                    print ""

                # Check for Public Holiday
                elif self.checkOnHolidays(currDate, holidayMap, employee, att_utility_pool) is True:
                    attSummaryLine.holidays_days = attSummaryLine.holidays_days + 1

                elif dutyTimeMap.get(self.getStrFromDate(currDate)): # Check this date is week end or not. If it is empty, then means this day is weekend
                    currentDaydutyTime = dutyTimeMap.get(self.getStrFromDate(currDate))
                    attendanceDayList = att_utility_pool.getAttendanceListByDay(attendance_data, currDate, currentDaydutyTime, day, dutyTimeMap)
                    attSummaryLine = self.makeDecision(attSummaryLine, attendanceDayList, currDate, currentDaydutyTime, employee, graceTime, holidayMap, empJoiningDateMap, att_utility_pool)
                else:
                    attSummaryLine = self.buildWeekEnd(attSummaryLine, currDate)

                currDate = currDate + day
        else:
            attSummaryLine.is_entered_rostering = 0

        noOfDays = (endDate - startDate).days + 1

        attSummaryLine = self.checkConsecutiveAbsence(attSummaryLine)

        get_extra_ot = self.getExtraOT(startDate, endDate, employeeId)

        self.saveAttSummary(employeeId, summaryId, noOfDays, attSummaryLine, get_extra_ot)

    def checkConsecutiveAbsence(self, attSummaryLine):

        if len(attSummaryLine.absent_days) > 1:
            day1 = datetime.timedelta(days=1)
            weekend_days = []
            consecutive = False
            for wkd in attSummaryLine.weekend_days:
                weekend_days.append(wkd.date)
            for abs_day in attSummaryLine.absent_days:
                if (abs_day.date + day1) in weekend_days:
                    consecutive = True
                    next_expected_abs = abs_day.date + day1 + day1

                if consecutive and (abs_day.date == next_expected_abs):
                    attSummaryLine.absent_days.append(TempAbsentDay(abs_day.date - day1))

        return attSummaryLine

    def makeDecision(self, attSummaryLine, attendanceDayList, currDate, currentDaydutyTime, employee, graceTime, holidayMap, empJoiningDateMap, att_utility_pool):

        employeeId = employee.id

        # Check for Holiday
        if self.checkOnHolidays(currDate, holidayMap, employee, att_utility_pool) is True:
            attSummaryLine.holidays_days = attSummaryLine.holidays_days + 1
            return attSummaryLine

        # Check for Personal Leave
        if att_utility_pool.checkOnPersonalLeave(employeeId, currDate) is True:
            attSummaryLine.leave_days = attSummaryLine.leave_days + 1
            return attSummaryLine

        # Check for Unpaid Leave
        if att_utility_pool.checkOnUnpaidLeave(employeeId, currDate) is True:
            attSummaryLine.unpaid_holidays = attSummaryLine.unpaid_holidays + 1
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
            if empJoiningDateMap.get(employeeId):
                joiningDate = empJoiningDateMap.get(employeeId)
                if self.getDateFromStr(joiningDate) <= currDate:
                    attSummaryLine = self.buildAbsentDetails(attSummaryLine, currentDaydutyTime, currDate,
                                                             totalPresentTime, attendanceDayList)
            else:
                attSummaryLine = self.buildAbsentDetails(attSummaryLine, currentDaydutyTime, currDate, totalPresentTime, attendanceDayList)

        return attSummaryLine

    def process(self, employeeIds, summaryId, operating_unit_id):
        att_utility_pool = self.env['attendance.utility']
        graceTime = att_utility_pool.getGraceTime(datetime.datetime.now())

        startDate = self.getAccountPeriodDate(summaryId).values()[0]
        endDate = self.getAccountPeriodDate(summaryId).values()[1]
        if employeeIds:
            empJoiningDateMap = self.getJoingDate(startDate, endDate, employeeIds)
        for empId in employeeIds:
            self.get_summary_data(empId, summaryId, graceTime, operating_unit_id, att_utility_pool,empJoiningDateMap)


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
        self._cr.execute(self.attendance_query, (employeeId, att_time_start, att_time_end,
                                                 employeeId, att_time_start, att_time_end,
                                                 employeeId, att_time_start, att_time_end))
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




    def saveAttSummary(self, employeeId, summaryId, noOfDays, attSummaryLine, get_extra_ot):

        summary_line_pool = self.env['hr.attendance.summary.line']
        weekend_pool = self.env['hr.attendance.weekend.day']
        absent_pool = self.env['hr.attendance.absent.day']
        absent_time_pool = self.env['hr.attendance.absent.time']
        late_day_pool = self.env['hr.attendance.late.day']
        late_time_pool = self.env['hr.attendance.late.time']

        ############## Save Summary Lines ######################
        salaryDays = noOfDays - len(attSummaryLine.absent_days)
        calOtHours = attSummaryLine.schedule_ot_hrs + get_extra_ot

        if attSummaryLine.schedule_ot_hrs > attSummaryLine.late_hrs:
            calOtHours = attSummaryLine.schedule_ot_hrs - attSummaryLine.late_hrs

        deductionRule = self.getLateSalaryDeductionRule()

        if deductionRule == 0:
            deduction_days = 0
        else:
            deduction_days = int(len(attSummaryLine.late_days) / deductionRule)

        vals = {'employee_id':      employeeId,
                'att_summary_id':   summaryId,
                'salary_days':      salaryDays,
                'present_days':     attSummaryLine.present_days,
                'nis_days':         attSummaryLine.nis_days,
                'holidays_days':    attSummaryLine.holidays_days,
                'leave_days':       attSummaryLine.leave_days,
                'unpaid_holidays':  attSummaryLine.unpaid_holidays,
                'absent_deduction_days': len(attSummaryLine.absent_days),
                'deduction_days':   deduction_days,
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


    def getExtraOT(self, startDate, endDate, employeeId):

        startDateTime = startDate + datetime.timedelta(seconds=1)
        endDateTime = endDate + datetime.timedelta(hours=23,minutes=59)

        self._cr.execute(self.getExtraOTQuery, (startDateTime, endDateTime, employeeId))
        get_query_extra_ot = self._cr.fetchone()

        get_extra_ot = get_query_extra_ot[0]
        if get_extra_ot:
            return get_extra_ot
        else:
            return 0

    def getJoingDate(self,startDate, endDate, employeeIds):
        query = """SELECT 
                        initial_employment_date, id 
                   FROM 
                        hr_employee
                   WHERE 
                        initial_employment_date > %s AND initial_employment_date <= %s AND id IN %s"""
        self._cr.execute(query, (self.getStrFromDate(startDate) , self.getStrFromDate(endDate) , tuple(employeeIds)))
        query_res = self._cr.fetchall()
        query_res_map = {}
        for i, line in enumerate(query_res):
            query_res_map[line[1]] = line[0]

        return query_res_map

    def getLateSalaryDeductionRule(self):

        query = """SELECT 
                         late_salary_deduction_rule
                    FROM
                         hr_attendance_config_settings 
                    order by id desc limit 1"""

        self._cr.execute(query, (tuple([])))
        deduction_rule_value = self._cr.fetchone()

        if not deduction_rule_value:
            return 0

        return deduction_rule_value[0]


    def getAccountPeriodDate(self,summaryId):
        self._cr.execute(self.period_query, (summaryId,))
        accountPeriod = self._cr.fetchall()
        if accountPeriod:
            result = {
                'startDate' : self.getDateFromStr(accountPeriod[0][0]),
                'endDate' : self.getDateFromStr(accountPeriod[0][1])
            }

            return result

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