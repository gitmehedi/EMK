from openerp import api, fields, models

class HrAttendanceImportError(models.Model):
    _name = 'hr.attendance.import.error'
    
    employee_code = fields.Char(string='Employee Code')
    employee_id =  fields.Integer(string='Employee ID', required=False) # ERP system employee ID
    check_in = fields.Char(string='Check In', required=False)
    check_out = fields.Char(string='Check Out', required=False)
    attempt_to_success = fields.Integer(string='Try', default=0)
    # attendance_server_id will be deprecated after 02-08-2017. operating_unit_id will fill
    #attendance_server_id = fields.Integer(string='Server Id', required=False)
    operating_unit_id = fields.Integer(string='Operating Unit Id', required=False)
    import_id = fields.Many2one('hr.attendance.import', 'id', ondelete='cascade')
    reason = fields.Char(string='Reason', required=False)
    
    