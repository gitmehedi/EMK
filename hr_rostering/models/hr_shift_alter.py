from openerp import models, fields,_,SUPERUSER_ID
from openerp import api
from openerp.exceptions import UserError, ValidationError


class HRShiftAlter(models.Model):
    _name = 'hr.shift.alter'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    # domain = "[('department_id', '=', department_id)]"
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True,default=_default_employee)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department', store=True)

    alter_date = fields.Date(string='Alter Date')
    duty_start = fields.Datetime(string='Duty Start',required=True)
    duty_end = fields.Datetime(string='Duty End',required=True)
    is_included_ot = fields.Boolean(string='Is OT')

    my_menu_check = fields.Boolean(string='Check',readonly=True)

    ot_start = fields.Datetime(string='OT Start')
    ot_end = fields.Datetime(string='OT End')
    grace_time = fields.Float(string='Grace Time', default='1.5')

    manager_id = fields.Many2one('hr.employee', string='Final Approval', readonly=True, copy=False)

    first_approval = fields.Boolean('First Approval', compute='compute_check_first_approval')

    user_id = fields.Many2one('res.users', string='User', related='employee_id.user_id', related_sudo=True, store=True,
                              default=lambda self: self.env.uid, readonly=True)

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('approved', "Approved"), 
        ('refuse', 'Refused'),
    ], default = 'draft',track_visibility='onchange')

    @api.multi
    def add_follower(self, employee_id):
        employee = self.env['hr.employee'].browse(employee_id)
        if employee.user_id:
            self.message_subscribe_users(user_ids=employee.user_id.ids)

    @api.model
    def create(self, vals):
        res = super(HRShiftAlter, self).create(vals)
        res._notify_approvers()
        return res

    ### mail notification
    @api.multi
    def _notify_approvers(self):
        """Input: res.user"""
        self.ensure_one()
        approvers = self.employee_id._get_employee_manager()
        if not approvers:
            return True
        for approver in approvers:
            self.sudo(SUPERUSER_ID).add_follower(approver.id)
            if approver.sudo(SUPERUSER_ID).user_id:
                self.sudo(SUPERUSER_ID)._message_auto_subscribe_notify(
                    [approver.sudo(SUPERUSER_ID).user_id.partner_id.id])
        return True

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

            ### User and state wise approve button hide function
    @api.multi
    def compute_check_first_approval(self):
        user = self.env.user.browse(self.env.uid)
        for h in self:
            if h.state != 'confirmed':
                h.first_approval = False
            ### no one can approve own request
            elif h.employee_id.user_id.id == self.env.user.id:
                h.first_approval = False
            elif user.has_group('hr_attendance.group_hr_attendance_user'):
                h.first_approval = True
            else:
                res = h.employee_id.check_1st_level_approval()
                h.first_approval = res