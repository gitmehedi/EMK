from openerp import models, fields,_
from openerp import api
from openerp.exceptions import UserError, ValidationError


class HRShiftAlter(models.Model):
    _name = 'hr.shift.alter'
    _rec_name = 'employee_id'

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    # domain = "[('department_id', '=', department_id)]"
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True,default=_default_employee)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department', store=True)

    alter_date = fields.Date(string='Alter Date')
    duty_start = fields.Datetime(string='Duty Start')
    duty_end = fields.Datetime(string='Duty End')
    is_included_ot = fields.Boolean(string='Is OT')

    my_menu_check = fields.Boolean(string='Check',readonly=True)

    ot_start = fields.Datetime(string='OT Start')
    ot_end = fields.Datetime(string='OT End')
    grace_time = fields.Float(string='Grace Time', default='1.5')

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

        # Show a msg for applied & approved state should not be delete

    @api.multi
    def unlink(self):
        for a in self:
            if a.state != 'draft':
                raise UserError(_('You can not delete this.'))
        return super(HRShiftAlter, self).unlink()