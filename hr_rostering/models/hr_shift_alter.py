from openerp import models, fields,_
from openerp import api
from openerp.exceptions import UserError, ValidationError


class HRShiftAlter(models.Model):
    _name = 'hr.shift.alter'
    _rec_name = 'employee_id'


    # user access funtion
    def _employee_check_hr_manager(self):
        user = self.env.user.browse(self.env.uid)
        if user.has_group('hr.group_hr_manager'):
            return True
        else:
            return False

    def _employee_check_user(self):
        user = self.env.user.browse(self.env.uid)
        if user.has_group('base.group_user'):
            return True
        else:
            return False


    def _employee_check_dept_manager(self):
        user = self.env.user.browse(self.env.uid)
        if user.has_group('gbs_base_package.group_dept_manager'):
            return True
        else:
            return False


    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    # domain = "[('department_id', '=', department_id)]"
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True,default=_default_employee)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department', store=True)

    alter_date = fields.Date(string='Alter Date')
    duty_start = fields.Datetime(string='Duty Start')
    duty_end = fields.Datetime(string='Duty End')
    is_included_ot = fields.Boolean(string='Is OT')

    ot_start = fields.Datetime(string='OT Start')
    ot_end = fields.Datetime(string='OT End')
    grace_time = fields.Float(string='Grace Time', default='1.5')

    # user access fields
    user_access_hr_manager = fields.Boolean(string='User Access Hr Manager',default=_employee_check_hr_manager)
    user_access_dept_manager = fields.Boolean(string='User Access Department Manager',default=_employee_check_dept_manager)
    user_access = fields.Boolean(string='User Access Normal',default=_employee_check_user)

    manager_id = fields.Many2one('hr.employee', string='Final Approval', readonly=True, copy=False)

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('approved', "Approved"), 
        ('refuse', 'Refused'),
    ], default = 'draft')

    @api.onchange('user_access_dept_manager')
    def onchange_user_access_dept_manager(self):
        if self.user_access_hr_manager!=True and self.user_access_dept_manager:
            return {'domain': {'employee_id': [('department_id.manager_id.user_id','=',self.env.user.id)]}}
        else:
            return {'domain': {'employee_id': [('company_id', '=', self.env.user.company_id.id )]}}

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