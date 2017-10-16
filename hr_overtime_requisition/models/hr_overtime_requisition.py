from openerp import api
from openerp import models, fields,_,SUPERUSER_ID
import datetime
from openerp.exceptions import UserError, ValidationError


class HROTRequisition(models.Model):
    _name='hr.ot.requisition'
    _inherit = ['mail.thread','ir.needaction_mixin']
    _rec_name = 'employee_id'

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one('hr.employee', string='Employee', index=True, readonly=True,
                                  default=_default_employee,required=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department',
                                    readonly=True, store=True)
    from_datetime = fields.Datetime('Start Date', readonly=True, index=True, copy=False,required=True)
    to_datetime = fields.Datetime('End Date', readonly=True, copy=False,required=True)
    total_hours = fields.Float(string='Total hours', compute='_compute_total_hours', store=True,digits=(15, 2),readonly=True)
    ot_reason = fields.Text(string='Reason for OT')

    first_approval = fields.Boolean('First Approval', compute='compute_check_first_approval')

    user_id = fields.Many2one('res.users', string='User', related='employee_id.user_id', related_sudo=True, store=True,
                              default=lambda self: self.env.uid, readonly=True)

    state = fields.Selection([
        ('to_submit', "To Submit"),
        ('to_approve', "To Approve"),
        ('hr_approve', "HR Approve"),
        ('approved', "Approved"),
        ('refuse', 'Refused'),
    ], default='to_submit',track_visibility='onchange')

    @api.multi
    def add_follower(self, employee_id):
        employee = self.env['hr.employee'].browse(employee_id)
        if employee.user_id:
            self.message_subscribe_users(user_ids=employee.user_id.ids)

    @api.model
    def create(self, vals):
        res = super(HROTRequisition, self).create(vals)
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


    @api.constrains('from_datetime','to_datetime')
    def _check_to_datetime_validation(self):

        for ot in self:
            if ot.to_datetime < ot.from_datetime:
                raise ValidationError(_("End Time can not less then Start Time!!"))

        domain = [
            ('from_datetime', '<=', ot.to_datetime),
            ('to_datetime', '>=', ot.from_datetime),
            ('employee_id', '=', ot.employee_id.id),
            ('id', '!=', ot.id),
            ('state', 'not in', ['refuse']),
        ]
        domainOT = self.search_count(domain)
        if domainOT:
            raise ValidationError(_('You can not have multiple OT requisition on same day!'))

    @api.depends('from_datetime', 'to_datetime')
    def _compute_total_hours(self):
        if self.from_datetime and self.to_datetime:
            start_dt = fields.Datetime.from_string(self.from_datetime)
            finish_dt = fields.Datetime.from_string(self.to_datetime)
            diff=finish_dt-start_dt
            hours = float(diff.total_seconds()  / 3600)
            self.total_hours = hours

    @api.one
    @api.constrains('total_hours')
    def _check_values(self):
        if self.total_hours == 0.0:
            raise ValidationError(_('Duration time should not be zero!!'))

    @api.multi
    def action_submit(self):
        self.write({'state': 'to_approve'})

    @api.multi
    def action_hod_approve(self):
        self.write({'state': 'hr_approve'})

    @api.multi
    def action_hr_approve(self):
        self.write({'state': 'approved'})

    @api.multi
    def action_refuse(self):
        self.write({'state': 'refuse'})

    @api.multi
    def action_reset(self):
        self.write({'state': 'to_submit'})

    @api.multi
    def unlink(self):
        for a in self:
            if a.state != 'to_submit':
                raise UserError(_('You can not delete this.'))
            return super(HROTRequisition, self).unlink()

    ### Showing batch
    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['to_approve','hr_approve'])]

    ### User and state wise approve button hide function
    @api.multi
    def compute_check_first_approval(self):
        user = self.env.user.browse(self.env.uid)
        for h in self:
            if h.state != 'to_approve':
                h.first_approval = False
            ### no one can approve own request
            elif h.employee_id.user_id.id == self.env.user.id:
                h.first_approval = False
            elif user.has_group('hr_attendance.group_hr_attendance_user'):
                h.first_approval = True
            else:
                res = h.employee_id.check_1st_level_approval()
                h.first_approval = res