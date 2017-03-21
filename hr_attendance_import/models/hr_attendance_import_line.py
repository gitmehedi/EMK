from openerp import api, fields, models

class HrAttendanceImportLine(models.Model):
    _name = 'hr.attendance.import.line'
    
    employee_id = fields.Many2one('hr.employee')
    check_in = fields.Datetime(string='Check In')
    check_out = fields.Datetime(string='Check Out')
    import_id = fields.Many2one('hr.attendance.import', 'id', ondelete='cascade')
    
    