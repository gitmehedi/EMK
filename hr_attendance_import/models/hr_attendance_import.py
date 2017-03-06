from openerp import api,fields,models
from openerp.exceptions import ValidationError,Warning
from datetime import date


class AttendanceImport(models.Model):
    _name = 'hr.attendance.import'
    
    name = fields.Char(string='Name', required=True)
    import_creation_date_time = fields.Datetime(string='Imported Date',default=date.today(),required=True)
    
    """ Relational fields"""
    import_temp = fields.One2many('hr.attendance.import.temp', 'import_id')
    import_error_lines = fields.One2many('hr.attendance.import.error', 'import_id')
    lines = fields.One2many('hr.attendance.import.line', 'import_id')
    
    @api.multi
    def validated(self):

        attendance_obj = self.env['hr.attendance']
        
        """ Fetch all from line obj"""
        attendance_line_obj = self.env['hr.attendance.import.line'].search([])
        
        for i in attendance_line_obj:
            if i is not None:
                emp_pool = self.env['hr.employee'].search([('id','=',i.employee_id.id)])
        
                att_line_obj_search = attendance_line_obj.search([('employee_id','=',emp_pool.id)])
        
                vals_attendance = {}
            
                for alos in att_line_obj_search:
                    if alos is not None:                        
                        if alos.check_out < alos.check_in:
                            raise ValidationError(('Check Out time can not be previous date of Check In time'))
                        
                        vals_attendance['employee_id'] = alos.employee_id.id
                        vals_attendance['check_in'] = alos.check_in
                        vals_attendance['check_out'] = alos.check_out
                
                        attendance_obj.create(vals_attendance)
        
        """ Clearing line obj"""                
        attendance_line_obj.unlink()           
                        
    