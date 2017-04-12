from openerp import models, fields
from openerp import api
import datetime
from email import _name
from datetime import timedelta

from late_time import TempLateTime
from late_day import TempLateDay
from attendance_summary_line import TempAttendanceSummaryLine

class AttendanceSummary(models.Model):
    _name = 'hr.attendance.summary'
    _inherit = ['mail.thread']
    _description = 'Attendance and over time summary'    

    name = fields.Char(size=100, string='Title', required='True')
    period = fields.Many2one("account.period", "Period", required=True)
    state = fields.Selection([
        ('draft', "Draft"),
        ('generated', "Generated"),
        ('confirmed', "Confirmed"),
        ('approved', "Approved"),
    ], default='draft')


    """ Relational Fields """
    att_summary_lines = fields.One2many('hr.attendance.summary.line', 'att_summary_id', string='Summary Lines')
    
    @api.multi
    def action_generated(self):
        self.state = 'generated'        
    
# Start Bappy Code


    def get_shiftLines(self, shiftId):

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

    def get_shiftList(self, calendarList):
        shiftList = []
        day = datetime.timedelta(days=1)

        for i, calendar in enumerate(calendarList):
            if (len(calendarList) == i + 1):
                shiftList.append(Shift(self.getDateFromStr(calendarList[i][0]),
                                       self.getDateFromStr(calendarList[i][0]), calendarList[i][1],
                                       self.get_shiftLines(calendarList[i][1])))
            else:
                shiftList.append(Shift(self.getDateFromStr(calendarList[i][0]),
                                       self.getDateFromStr(calendarList[i + 1][0]) - day, calendarList[i][1],
                                       self.get_shiftLines(calendarList[i][1])))

        return shiftList

    def build_dutyTime(self, preStartDate, postEndDate, shiftList):
        dutyTimeMap = {}
        day = datetime.timedelta(days=1)
        while preStartDate <= postEndDate:
            for i, shift in enumerate(shiftList):
                if shift.effectiveDtStr <= preStartDate <= shift.effectiveDtEnd:
                    if shift.shiftLines.get(preStartDate.weekday()):
                        startTime = shift.shiftLines.get(preStartDate.weekday()).startTime
                        endTime = shift.shiftLines.get(preStartDate.weekday()).endTime
                        startDutyTime = preStartDate + timedelta(hours=startTime)
                        if startTime > endTime:
                            endDutyTime = preStartDate + timedelta(hours=endTime + 24)
                        else:
                            endDutyTime = preStartDate + timedelta(hours=endTime)
                        dutyTimeMap[preStartDate.strftime('%Y.%m.%d')] = DutyTime(startDutyTime, endDutyTime)
                        break
            preStartDate = preStartDate + day
        return dutyTimeMap

    def print_dutyTime(self, preStartDate, postEndDate, dutyTimeMap):
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
    def get_previousDutyTime(self, date, dutyTimeMap):
        previousDayDutyTime = dutyTimeMap.get(self.getStrFromDate(date))
        if previousDayDutyTime:
            return previousDayDutyTime
        else:
            previousDayDutyTime = DutyTime(date + timedelta(hours=22), date + timedelta(hours=23))
            return previousDayDutyTime

    # Get next duty time. If previous duty time is null that means this day was weekend.
    # Then set a default time at previous day
    def get_nextDutyTime(self, date, dutyTimeMap):
        nextDutyTime = dutyTimeMap.get(self.getStrFromDate(date))
        if nextDutyTime:
            return nextDutyTime
        else:
            nextDutyTime = DutyTime(date + timedelta(hours=23.9), date + timedelta(hours=23.95))
            return nextDutyTime

    def buildAbsentDayDetails(self, date, workingHours, otHours, absentSummary, currentDaydutyTime,
                              attendanceDayList, employeeId):

        absentSummary.absent_days = absentSummary.absent_days + 1
        absentSummary.ot_hours = absentSummary.ot_hours + otHours
        absentSummary.employee_id = employeeId
        absentSummary.absent_day_list.append(TempLateDay(date, currentDaydutyTime.startDutyTime,
                                                         currentDaydutyTime.endDutyTime,
                                                         currentDaydutyTime.startDutyTime,
                                                         currentDaydutyTime.endDutyTime,
                                                         currentDaydutyTime.dutyMinutes / 60,
                                                         workingHours, attendanceDayList))
        return absentSummary

    def saveAbsentSummary(self, absentSummary):

        att_summary_pool = self.env['hr.absent.summary']
        att_day_pool = self.env['hr.absent.day']
        att_pool = self.env['hr.absent.attendance.day']

        vals = {'absent_days': absentSummary.absent_days,
                'ot_hours': absentSummary.ot_hours,
                'employee_id': absentSummary.employee_id
                }
        res = att_summary_pool.create(vals)
        absent_summary_id = res.id

        for i, absentDay in enumerate(absentSummary.absent_day_list):

            vals1 = {'date': absentDay.date, 'scheduleTimeStart': absentDay.scheduleTimeStart,
                     'scheduleTimeEnd': absentDay.scheduleTimeEnd,
                     'otTimeStart': absentDay.otTimeStart, 'otTimeEnd': absentDay.otTimeEnd,
                     'scheduleWorkingHours': absentDay.scheduleWorkingHours,
                     'workingHours': absentDay.workingHours, 'absent_summary_id': absent_summary_id
                     }
            res = att_day_pool.create(vals1)
            absent_day_id = res.id

            for i, attendance in enumerate(absentDay.attendance_day_list):
                vals2 = {'check_in': attendance.check_in, 'check_out': attendance.check_out,
                         'duration': attendance.duration, 'absent_day_id': absent_day_id
                         }
                res = att_pool.create(vals2)

    def getDateFromStr(self, dateStr):
        return datetime.datetime.strptime(dateStr, "%Y-%m-%d")

    def getStrFromDate(self, date):
        return date.strftime('%Y.%m.%d')

    def getDateTimeFromStr(self, dateStr):
        return datetime.datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S")

    @api.multi
    def get_summary_data(self):

        dutyTimeMap = {}
        shiftList = []

        startDate = datetime.datetime(2017, 02, 01, 0, 0)
        endDate = datetime.datetime(2017, 02, 28, 0, 0)
        absentGraceMinutes = 10
        employeeId = 2
        absentSummary = TempAttendanceSummaryLine()

        day = datetime.timedelta(days=1)

        preStartDate = startDate - day
        postEndDate = endDate + day

        # Getting Calendar Id for each employee
        calendar_query = """SELECT effective_from, shift_id
                    FROM
                      hr_shifting_history
                    WHERE
                        employee_id = 2 AND
                        effective_from BETWEEN %s AND %s
                    ORDER BY
                        effective_from ASC"""

        self._cr.execute(calendar_query, (preStartDate, postEndDate))
        calendarList = self._cr.fetchall()

        if calendarList:
            shiftList = self.get_shiftList(calendarList)
            if shiftList:
                dutyTimeMap = self.build_dutyTime(preStartDate, postEndDate, shiftList)
                self.print_dutyTime(preStartDate, postEndDate, dutyTimeMap)

        attendance_query = """SELECT
                                    check_in, check_out, worked_hours
                              FROM
                                  hr_attendance
                              WHERE check_out > %s
                              AND check_in < %s
                              AND employee_id = 2
                              ORDER BY check_in ASC"""

        self._cr.execute(attendance_query, (dutyTimeMap.get(self.getStrFromDate(preStartDate)).endDutyTime,
                                            dutyTimeMap.get(self.getStrFromDate(postEndDate)).startDutyTime))
        attendance_data = self._cr.fetchall()

        while startDate <= endDate:
            # Check this date is week end or not. If it is empty, then means this day is weekend
            currentDaydutyTime = dutyTimeMap.get(self.getStrFromDate(startDate))
            if currentDaydutyTime:
                attendanceDayList = []
                previousDayDutyTime = self.get_previousDutyTime(startDate - day, dutyTimeMap)
                nextDayDutyTime = self.get_nextDutyTime(startDate + day, dutyTimeMap)
                temp_attendance_data = list(attendance_data)
                for i, attendance in enumerate(attendance_data):
                    if previousDayDutyTime.endDutyTime < self.getDateTimeFromStr(
                            attendance[0]) < currentDaydutyTime.endDutyTime and \
                                            currentDaydutyTime.startDutyTime < self.getDateTimeFromStr(
                                        attendance[1]) < nextDayDutyTime.startDutyTime:
                        attendanceDayList.append(TempLateTime(attendance[0], attendance[1], attendance[2]))
                        temp_attendance_data.remove(attendance)
                    # If attendance data is greater then 48 hours from current date (startDate) then call break.
                    # Means rest of the attendance date are not illegible for current date. Break condition apply for better optimization
                    elif (self.getDateTimeFromStr(attendance[0]) - startDate).total_seconds() / 60 / 60 > 48:
                        break
                attendance_data = temp_attendance_data
                if attendanceDayList:
                    totalMinute = 0
                    # Collect date wise in out data
                    for i, attendanceDay in enumerate(attendanceDayList):
                        ch_in = self.getDateTimeFromStr(attendanceDay.check_in)
                        ch_out = self.getDateTimeFromStr(attendanceDay.check_out)
                        if ch_in < currentDaydutyTime.startDutyTime:
                            ch_in = currentDaydutyTime.startDutyTime
                        if ch_out > currentDaydutyTime.endDutyTime:
                            ch_out = currentDaydutyTime.endDutyTime
                        totalMinute = totalMinute + (ch_out - ch_in).total_seconds() / 60

                    print(">>>>", startDate, ">>Working Hour<<", totalMinute / 60, "List:", len(attendanceDayList))
                    workingMinutes = currentDaydutyTime.dutyMinutes - totalMinute
                    if workingMinutes > absentGraceMinutes:
                        otHours = 5
                        absentSummary = self.buildAbsentDayDetails(startDate, totalMinute / 60, otHours,
                                                                   absentSummary, currentDaydutyTime, attendanceDayList,
                                                                   employeeId)
                else:
                    # @Todo- Need to consider personal leave and holidays
                    print(">>>>", startDate, ">>Not Present<<")
            else:
                print(">>>>", startDate, ">>WeekEnd<<")
            startDate = startDate + day

        self.saveAbsentSummary(absentSummary)

    # End Bappy Code
    
    @api.multi
    def action_draft(self):
        self.state = 'draft'
        
    @api.multi
    def action_confirm(self):
        for attendance in self:
            attendance.state = 'confirmed'
            
    @api.multi
    def action_done(self):
        for attendance in self:
            self.state = 'approved'


# Start Code Bappy
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
    def __init__(self, startDutyTime=None, endDutyTime=None):
        self.startDutyTime = startDutyTime
        self.endDutyTime = endDutyTime
        self.dutyMinutes = (endDutyTime - startDutyTime).total_seconds() / 60

        # End Code Bappy