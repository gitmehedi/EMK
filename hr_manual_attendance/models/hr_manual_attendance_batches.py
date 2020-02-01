from openerp import api
from openerp import models, fields, _, SUPERUSER_ID
import datetime
from openerp.exceptions import UserError, ValidationError


class HrManualAttendance(models.Model):
    _name = 'hr.manual.attendance.batches'
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

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, default=_default_employee)
    reason = fields.Text(string='Reason')
    department_id = fields.Many2one('hr.department', related='employee_id.department_id',
                                    string='Department', store=True)
    manager_id = fields.Many2one('hr.employee', string='Employee Manager',
                                 related='employee_id.parent_id')
    approver_id = fields.Many2one('res.users', string='Approvar', readonly=True, copy=False,
                                  help='This field is automatically filled by the user who validate the manual attendance request')
    my_menu_check = fields.Boolean(string='Check',readonly=True)
    can_reset = fields.Boolean('Can reset', compute='_compute_can_reset')
    user_id = fields.Many2one('res.users', string='User', related='employee_id.user_id', related_sudo=True, store=True,
                              default=lambda self: self.env.uid, readonly=True)
    pending_approver = fields.Many2one('hr.employee', string="Pending Approver", readonly=True,
                                       default=_default_approver)
    pending_approver_user = fields.Many2one('res.users', string='Pending approver user',
                                            related='pending_approver.user_id', related_sudo=True, store=True,
                                            readonly=True)
    current_user_is_approver = fields.Boolean(string='Current user is approver',
                                              compute='_compute_current_user_is_approver')
    approbations_ids = fields.One2many('hr.employee.manual.att.approbation', 'manual_attandance_batches_id', string='Approvals',
                        readonly=True)
    line_ids = fields.One2many('hr.manual.attendance', 'parent_id', string='Manual Attendance')


    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('refuse', 'Refused'),
        ('validate', 'Approved')
    ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
        help="The status is set to 'To Submit', when a manual attendance request is created." +
             "\nThe status is 'To Approve', when manual attendance request is confirmed by user." +
             "\nThe status is 'Refused', when manual attendance request is refused by manager." +
             "\nThe status is 'Approved', when manual attendance request is approved by manager.")


    @api.multi
    def add_follower(self, employee_id):
        employee = self.env['hr.employee'].browse(employee_id)
        if employee.user_id:
            self.message_subscribe_users(user_ids=employee.user_id.ids)

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
    def _compute_can_reset(self):
        """ User can reset a leave request if it is its own leave request or if he is a Manager."""
        user = self.env.user
        group_hr_manager = self.env.ref('hr_attendance.group_hr_attendance_user')
        for att in self:
            if group_hr_manager in user.groups_id or att.employee_id and att.employee_id.user_id == user:
                att.can_reset = True


    @api.multi
    def action_confirm(self):
        if self.filtered(lambda manual_attendance: manual_attendance.state != 'draft'):
            raise UserError(_('Manual Attendance request must be in Draft state ("To Submit") in order to confirm it.'))
        # self.line_ids.write({'state': 'confirm'})
        self.line_ids.action_confirm()
        return self.write({'state': 'confirm'})

    @api.multi
    def action_approve(self):
        for manual_attendance in self:
            if manual_attendance.state != 'confirm':
                raise UserError(_('Manual Attendance Request must be confirmed ("To Approve") in order to approve it.'))
            is_last_approbation = False
            sequence = 0
            next_approver = None
            for approver in manual_attendance.employee_id.holidays_approvers:
                sequence = sequence + 1
                if manual_attendance.pending_approver.id == approver.approver.id:
                    if sequence == len(manual_attendance.employee_id.holidays_approvers):
                        is_last_approbation = True
                    else:
                        next_approver = manual_attendance.employee_id.holidays_approvers[sequence].approver
            if is_last_approbation:
                manual_attendance.action_validate()
            else:
                vals = {'state': 'confirm'}
                if next_approver and next_approver.id:
                    vals['pending_approver'] = next_approver.id
                manual_attendance.write(vals)
                self.env['hr.employee.manual.att.approbation'].create(
                    {'manual_attandance_batches_id': manual_attendance.id, 'approver': self.env.uid, 'sequence': sequence,
                     'date': fields.Datetime.now()})


    @api.multi
    def action_validate(self):
            self.write({'state': 'validate'})
            for rec in self.line_ids:
                rec.action_validate()

    @api.multi
    def action_refuse(self):
        for manual_attendance in self:
            if self.state not in ['confirm', 'validate']:
                raise UserError(_('Manual Attendance request must be confirmed or validated in order to refuse it.'))
            manual_attendance.write({'state': 'refuse'})
            manual_attendance.line_ids.write({'state': 'refuse'})
        return True

    @api.multi
    def action_draft(self):
        for att in self:
            att.write({'state': 'draft'})
            att.line_ids.write({'state': 'draft'})
        return True

    ####################################################
    # Override methods
    ####################################################

    @api.model
    def create(self, vals):
        if vals.get('employee_id', False):
            employee = self.env['hr.employee'].browse(vals['employee_id'])
            if employee and employee.holidays_approvers and employee.holidays_approvers[0]:
                vals['pending_approver'] = employee.holidays_approvers[0].approver.id
        res = super(HrManualAttendance, self).create(vals)
        res._notify_approvers()
        return res

    @api.multi
    def write(self, values):
        employee_id = values.get('employee_id', False)
        if employee_id:
            self.pending_approver = self.env['hr.employee'].search([('id', '=', employee_id)]).holidays_approvers[
                0].approver.id
        res = super(HrManualAttendance, self).write(values)
        return res

    @api.multi
    def unlink(self):
        for m in self:
            if m.state != 'draft':
                raise UserError(_('You can not delete this.'))
        return super(HrManualAttendance, self).unlink()

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

