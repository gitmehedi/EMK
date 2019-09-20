from openerp import models, fields,_,SUPERUSER_ID
from openerp import api
from openerp.exceptions import UserError, ValidationError


class HRShiftAlter(models.Model):
    _name = 'hr.shift.alter'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    @api.multi
    def _default_approver(self):
        default_approver = 0
        employee = self._default_employee()
        if isinstance(employee, int):
            emp_obj = self.env['hr.employee'].search([('id', '=', employee)], limit=1)
            if emp_obj.sudo().holidays_approvers:
                default_approver = emp_obj.sudo().holidays_approvers[0].approver.id
        else:
            if employee.sudo().holidays_approvers:
                default_approver = employee.sudo().holidays_approvers[0].approver.id
        return default_approver

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True,default=_default_employee,ondelete="cascade",track_visibility='onchange')
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department', store=True,ondelete="cascade")
    alter_date = fields.Date(string='Alter Date', required=True, track_visibility='onchange')
    duty_start = fields.Datetime(string='Duty Start',required=True, track_visibility='onchange')
    duty_end = fields.Datetime(string='Duty End',required=True, track_visibility='onchange')
    is_included_ot = fields.Boolean(string='Is OT', track_visibility='onchange')
    my_menu_check = fields.Boolean(string='Check',readonly=True)
    ot_start = fields.Datetime(string='OT Start', track_visibility='onchange')
    ot_end = fields.Datetime(string='OT End', track_visibility='onchange')
    grace_time = fields.Float(string='Grace Time', default='1.5', track_visibility='onchange')
    user_id = fields.Many2one('res.users', string='User', related='employee_id.user_id', related_sudo=True, store=True,
                              default=lambda self: self.env.uid, readonly=True,ondelete="cascade")

    pending_approver = fields.Many2one('hr.employee', string="Pending Approver", readonly=True,
                                       default=_default_approver)
    pending_approver_user = fields.Many2one('res.users', string='Pending approver user',
                                            related='pending_approver.user_id', related_sudo=True, store=True,
                                            readonly=True)
    current_user_is_approver = fields.Boolean(string='Current user is approver',
                                              compute='_compute_current_user_is_approver')
    approbations = fields.One2many('hr.employee.alter.approbation', 'alter_ids', string='Approvals', readonly=True)

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('approved', "Approved"),
        ('refuse', 'Refused'),
    ], default = 'draft',track_visibility='onchange')

    ####################################################
    # Business methods
    ####################################################

    @api.onchange('is_included_ot')
    def _onchange_is_included_ot(self):
        if self.is_included_ot == False:
            self.ot_start = None
            self.ot_end = None

    @api.onchange('employee_id')
    def _onchange_employee(self):
        if self.employee_id and self.employee_id.holidays_approvers:
            self.pending_approver = self.employee_id.holidays_approvers[0].approver.id
        else:
            self.pending_approver = False

    @api.one
    def _compute_current_user_is_approver(self):
        if self.pending_approver.user_id.id == self.env.user.id:
            self.current_user_is_approver = True
        else:
            self.current_user_is_approver = False

    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'

    @api.multi
    def action_approve(self):
        for alter in self:
            is_last_approbation = False
            sequence = 0
            next_approver = None
            for approver in alter.employee_id.holidays_approvers:
                sequence = sequence + 1
                if alter.pending_approver.id == approver.approver.id:
                    if sequence == len(alter.employee_id.holidays_approvers):
                        is_last_approbation = True
                    else:
                        next_approver = alter.employee_id.holidays_approvers[sequence].approver
            if is_last_approbation:
                alter.action_validate()
            else:
                vals = {'state': 'confirmed'}
                if next_approver and next_approver.id:
                    vals['pending_approver'] = next_approver.id
                alter.write(vals)
                self.env['hr.employee.alter.approbation'].create({'alter_ids': alter.id, 'approver': self.env.uid, 'sequence': sequence, 'date': fields.Datetime.now()})

    @api.multi
    def action_validate(self):
        for ot in self:
            ot.write({'state': 'approved'})

    @api.multi
    def action_refuse(self):
        self.write({'state': 'refuse'})

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def add_follower(self, employee_id):
        employee = self.env['hr.employee'].browse(employee_id)
        if employee.user_id:
            self.message_subscribe_users(user_ids=employee.user_id.ids)

    ####################################################
    # Override methods
    ####################################################

    @api.model
    def create(self, vals):
        if vals.get('employee_id', False):
            employee = self.env['hr.employee'].browse(vals['employee_id'])
            if employee and employee.holidays_approvers and employee.holidays_approvers[0]:
                vals['pending_approver'] = employee.holidays_approvers[0].approver.id
        res = super(HRShiftAlter, self).create(vals)
        res._notify_approvers()
        return res

    @api.multi
    def write(self, values):
        employee_id = values.get('employee_id', False)
        if employee_id:
            self.pending_approver = self.env['hr.employee'].search([('id', '=', employee_id)]).holidays_approvers[0].approver.id
        res = super(HRShiftAlter, self).write(values)
        return res

    @api.multi
    def unlink(self):
        for a in self:
            if a.state != 'draft':
                raise UserError(_('You can not delete this.'))
        return super(HRShiftAlter, self).unlink()

    ### mail notification
    @api.multi
    def _notify_approvers(self):
        approvers = self.employee_id._get_employee_manager()
        if not approvers:
            return True
        for approver in approvers:
            self.sudo(SUPERUSER_ID).add_follower(approver.id)
            if approver.sudo(SUPERUSER_ID).user_id:
                self.sudo(SUPERUSER_ID)._message_auto_subscribe_notify(
                    [approver.sudo(SUPERUSER_ID).user_id.partner_id.id])
        return True