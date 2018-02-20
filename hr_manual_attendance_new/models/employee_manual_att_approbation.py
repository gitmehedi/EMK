#-*- coding:utf-8 -*-
from odoo import models, fields

class EmployeeManualAttendanceApprobation(models.Model):
    _name = "hr.employee.manual.attendance.approbation"
    _order= "sequence"

    manual_attendance_id = fields.Many2one('hr.manual.attendance.batches', string='Manual Attendance', required=True,ondelete="cascade")
    approver = fields.Many2one('res.users', string='Approver', required=True,ondelete="cascade")
    sequence = fields.Integer(string='Approbation sequence', default=10, required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now())