from openerp import api,fields,models

from odoo.exceptions import UserError

class AttendanceImport(models.Model):
    _name = 'hr.attendance.import'
    
    name = fields.Char(string='Name', required=True)
    import_creation_date_time = fields.Datetime(string='Imported Date',required=True)
    
    """ Relational fields"""
    import_temp = fields.One2many('hr.attendance.import.temp', 'import_id')
    import_error_lines = fields.One2many('hr.attendance.import.error', 'import_id')
    lines = fields.One2many('hr.attendance.import.line', 'import_id')
    