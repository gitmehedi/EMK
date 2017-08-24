from odoo import api, fields, models,tools
import datetime
from datetime import timedelta


class Shift(object):
    def __init__(self, effectiveDtStr=None, effectiveDtEnd=None, shiftId=None, shiftLines=None):
        self.effectiveDtStr = effectiveDtStr
        self.effectiveDtEnd = effectiveDtEnd
        self.shiftId = shiftId
        self.shiftLines = shiftLines

class ShiftLine(object):
    def __init__(self, weekDay=None, startTime=None, endTime=None, isot=None, otStartTime=None, otEndTime=None,
                 graceTime=None):
        self.weekDay = int(weekDay)
        self.startTime = startTime
        self.endTime = endTime
        self.isot = isot
        self.otStartTime = otStartTime
        self.otEndTime = otEndTime
        self.graceTime = graceTime

class DutyTime(object):
    def __init__(self, startDutyTime=None, endDutyTime=None, isot=None, otStartDutyTime=None, otEndDutyTime=None,
                 graceTime=None):
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

class TempLateTime(object):

    def __init__(self, check_in=None, check_out=None, duration=None):
        self.check_in = check_in
        self.check_out = check_out
        self.duration = duration


class Employee(object):
    def __init__(self, employee, check_in=None):
        self.employeeId = employee.id
        self.name = employee.name
        self.dept = employee.department_id.name
        self.designation = employee.job_id.name
        self.check_in = check_in