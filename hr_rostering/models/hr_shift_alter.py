from openerp import api,fields,models
from datetime import date
import datetime


class HRShiftAlter(models.Model):
    _name = 'hr.shift.alter'
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', string="Employee", required = True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department', store=True)
    alter_date = fields.Date(string = 'Alter Date')
    alter_time_start = fields.Datetime(string = 'Alter Time Start')
    alter_time_end = fields.Datetime(string = 'Alter Time End')
    ot_time_start = fields.Datetime(string = 'Over Time Start')
    ot_time_end = fields.Datetime(string = 'Over Time End')
    ot_included = fields.Boolean(string='Is OT included')
    manager_id = fields.Many2one('hr.employee', string='Final Approval', readonly=True, copy=False)

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('approved', "Approved"), 
        ('refuse', 'Refused'),
    ], default = 'draft')
    
    @api.multi
    def action_approve(self):
        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)    
        self.write({'state': 'approved', 'manager_id': manager.id})
    
    @api.multi    
    def action_confirm(self):
        self.state = 'confirmed' 
    
    @api.multi
    def action_refuse(self):
        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)    
        self.write({'state': 'refuse', 'manager_id': manager.id})
                        
    @api.multi
    def action_draft(self):
        self.state = 'draft'
              
    


    
    