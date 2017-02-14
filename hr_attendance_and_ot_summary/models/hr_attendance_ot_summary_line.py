from openerp import models, fields
from openerp import api

class HrAttendanceOTSummaryLine(models.Model):    
    _name = 'hr.attendance.ot.summary.line'
    _description = 'Attendance and over time summary line'    
    
    attendance_1 = fields.Integer(string="Attendance 1")
    attendance_summary = fields.Integer(string="attendance summary")
    over_time_1 = fields.Integer(string="over time 1")
    over_time_summary = fields.Integer(string="over time summary")
    
    """ Relational Fields """
    
    parent_id = fields.Many2one('hr.attendance.ot.summary')
    employee_id = fields.Many2one('hr.employee', string="Employee ID")
    
