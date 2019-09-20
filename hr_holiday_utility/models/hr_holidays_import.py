from datetime import date
from odoo import api, models, fields

class HrHolidaysImport(models.Model):
    _name = 'hr.holidays.import'
    
    name = fields.Char(string='Name', required=True)
    import_creation_date_time = fields.Datetime(string='Imported Date',default=date.today(),required=True)
    
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('imported', "Imported")
    ], default='draft')
    
    """ Relational fields"""
    import_temp = fields.One2many('hr.holidays.import.temp', 'import_id',states={'imported': [('readonly', True)]})
    import_error_lines = fields.One2many('hr.holidays.import.error', 'import_id',states={'imported': [('readonly', True)]})
    lines = fields.One2many('hr.holidays.import.line', 'import_id',states={'imported': [('readonly', True)]})
    
    @api.multi
    def validated(self):
        holidays_pool = self.env['hr.holidays']
        holidays_import_line_pool = self.env['hr.holidays.import.line'].search([('import_id','=',self.id)])
        
        is_success = False
        vals = {}

        for line in holidays_import_line_pool:
            vals['name'] = line.name
            vals['holiday_status_id'] = line.holiday_status_id
            vals['employee_id'] = int(line.employee_id)
            vals['holiday_type'] = 'employee'
            vals['type'] = line.type
            #vals['state'] = 'validate'
            vals['number_of_days_temp'] = line.number_of_days

            if (line.type == 'add'):
                vals['number_of_days'] = line.number_of_days
            elif(line.type == 'remove'):
                vals['number_of_days'] = -int(line.number_of_days)

            holidays_pool.create(vals)

            is_success = True
            if is_success is True:
                self.state = 'imported'
                 
    
    @api.multi    
    def action_confirm(self):
        self.state = 'confirmed'
