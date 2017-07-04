from datetime import date
from openerp import models, fields,_
from openerp import api
from openerp.exceptions import UserError, ValidationError


class AttendanceImport(models.Model):
    _name = 'hr.attendance.import'
    
    name = fields.Char(string='Name', required=True)
    import_creation_date_time = fields.Datetime(string='Imported Date',default=date.today(),required=True)
    
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('imported', "Imported")
    ], default='draft')
    
    """ Relational fields"""
    import_temp = fields.One2many('hr.attendance.import.temp', 'import_id',states={'imported': [('readonly', True)]})
    import_error_lines = fields.One2many('hr.attendance.import.error', 'import_id',states={'imported': [('readonly', True)]})
    lines = fields.One2many('hr.attendance.import.line', 'import_id',states={'imported': [('readonly', True)]})
    
    @api.multi
    def validated(self):

        attendance_obj = self.env['hr.attendance']
        
        """ Fetch all from line obj"""
        attendance_line_obj = self.env['hr.attendance.import.line'].search([('import_id','=',self.id)])
        
        is_success = False

        for i in attendance_line_obj:
            if i is not None:
                emp_pool = self.env['hr.employee'].search([('id','=',i.employee_id.id)])

                att_line_obj_search = attendance_line_obj.search([('employee_id','=',emp_pool.id)])

                vals_attendance = {}
                vals_attendance['employee_id'] = i.employee_id.id
                vals_attendance['check_in'] = i.check_in
                vals_attendance['check_out'] = i.check_out

                attendance_obj.create(vals_attendance)
                is_success = True

            if is_success is True:
                self.state = 'imported'
                 
    
    @api.multi    
    def action_confirm(self):
        self.state = 'confirmed'

    # Show a msg for applied & approved state should not be delete
    @api.multi
    def unlink(self):
        for imp in self:
            if imp.state != 'draft':
                raise UserError(_('You can not delete this.'))
            imp.lines.unlink()
        return super(AttendanceImport, self).unlink()
