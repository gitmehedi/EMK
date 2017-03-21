from openerp import models, fields
from openerp import api

class HrAttendanceOTSummaryLine(models.Model):    
    _name = 'hr.attendance.ot.summary.line'
    _description = 'Attendance and over time summary line'    
    
    attendance_history = fields.Integer(string="Attendance History")
    attendance_summary = fields.Integer(string="Attendance Summary")
    over_time_history = fields.Integer(string="Overtime History")
    over_time_summary = fields.Integer(string="Overtime Summary")
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department', store=True)
    
    """ Relational Fields """
    
    parent_id = fields.Many2one('hr.attendance.ot.summary')
    employee_id = fields.Many2one('hr.employee', string="Employee ID")
    
