from openerp import api,fields,models

from odoo.exceptions import UserError

class AttendanceImport(models.Model):
    _name = 'hr.attendance.import'
    
    name = fields.Char(string='Name', required=True)
    import_creation_date_time = fields.Datetime(string='Imported Date',required=True)
    file_name= fields.Char(string='File')
    
    ## newly added fields
    import_temp = fields.One2many('hr.attendance.import.temp', 'import_id')
    import_error_lines = fields.One2many('hr.attendance.import.error', 'import_id')
    lines = fields.One2many('hr.attendance.import.line', 'import_id')
        
    @api.multi
    def import_lines(self):
        self.ensure_one()
        module = __name__.split('addons.')[1].split('.')[0]
        view = self.env.ref('%s.aml_import_view_form' % module)
        
        return {
            'name': _('Import File'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'aml.import',
            'view_id': False, #view.id,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
       