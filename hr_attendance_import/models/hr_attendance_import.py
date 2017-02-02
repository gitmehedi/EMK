from openerp import api
from openerp import fields
from openerp import models
from odoo.exceptions import UserError


class AttendanceImport(models.Model):
    #_inherit= 'account.move'
    _name = 'hr.attendance.import'
    
    name = fields.Char(string='Name')
    import_creation_date_time = fields.Datetime(string='Imported Date')
    file_name= fields.Char(string='File')
    
    @api.multi
    def process_imported_data(self):
        raise UserError(_('Not Implemented yet!'))
    
        
    """ @api.multi
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
    """    