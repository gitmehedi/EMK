from odoo import models, fields, api, SUPERUSER_ID
import logging
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

HOURS_PER_DAY = 8


class HrShortLeave(models.Model):
    _name = "hr.short.leave"
    _description = "Half Day Leaves "
    _order = "date_from desc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)

    def _default_leave_year(self):
        today = fields.Date.today()
        return self.env['date.range'].search([('type_id.holiday_year', '=', True),
                                              ('date_start', '<=', today), ('date_end', '>=', today)])

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

    name = fields.Char('Description')

    report_note = fields.Text('HR Comments')
    user_id = fields.Many2one('res.users', string='User', related='employee_id.user_id', related_sudo=True, store=True,
                              default=lambda self: self.env.uid, readonly=True)
    date_from = fields.Datetime('Start Time', readonly=True, index=True, copy=False, required=True,
                                track_visibility='onchange',
                                states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    date_to = fields.Datetime('End Time', readonly=True, copy=False, required=True, track_visibility='onchange',
                              states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string='Employee', index=True, readonly=True, required=True,
                                  states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
                                  default=_default_employee)
    notes = fields.Text('Reasons', readonly=True,
                        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    number_of_days = fields.Float('Number of Days', compute='_compute_total_hours', readonly=True, store=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department',
                                    readonly=True, store=True)
    can_reset = fields.Boolean('Can reset', compute='_compute_can_reset')

    pending_approver = fields.Many2one('hr.employee', string="Pending Approver", readonly=True,
                                       default=_default_approver)
    pending_approver_user = fields.Many2one('res.users', string='Pending approver user',
                                            related='pending_approver.user_id', related_sudo=True, store=True,
                                            readonly=True)
    current_user_is_approver = fields.Boolean(string='Current user is approver',
                                              compute='_compute_current_user_is_approver')
    approbations = fields.One2many('hr.employee.short.leave.approbation', 'short_leave_ids', string='Approvals',
                                   readonly=True)
    holiday_status_id = fields.Many2one("hr.holidays.status", string="Leave Type", required=True, readonly=True,
                                        domain="[('short_leave_flag','=',True)]",
                                        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    leave_year_id = fields.Many2one('date.range', string="Leave Year", default=_default_leave_year,
                                    domain="[('type_id.holiday_year', '=', True)]")

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate', 'Approved')
    ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
        help="The status is set to 'To Submit', when a holiday request is created." +
             "\nThe status is 'To Approve', when holiday request is confirmed by user." +
             "\nThe status is 'Refused', when holiday request is refused by manager." +
             "\nThe status is 'Approved', when holiday request is approved by manager.")

    ####################################################
    # Business methods
    ####################################################

    _sql_constraints = [
        ('date_check2', "CHECK ( (date_from <= date_to))", "The start date must be anterior to the end date."),
        ('date_check', "CHECK ( number_of_days >= 0 )", "The number of days must be greater than 0."),
    ]

    @api.depends('date_from', 'date_to')
    def _compute_total_hours(self):
        if self.date_from and self.date_to:
            start_dt = fields.Datetime.from_string(self.date_from)
            finish_dt = fields.Datetime.from_string(self.date_to)
            diff = finish_dt - start_dt
            hours = float(diff.total_seconds() / 3600)
            self.number_of_days = hours

    @api.one
    @api.constrains('number_of_days')
    def _check_number_of_hours(self):
        if self.number_of_days:
            if self.number_of_days > self.holiday_status_id.number_of_hours:
                raise ValidationError(
                    _('[Warning] Short leave cannot exceed %s hours' % self.holiday_status_id.number_of_hours))

    @api.multi
    def _compute_can_reset(self):
        """ User can reset a leave request if it is its own leave request or if he is an Hr Manager."""
        user = self.env.user
        group_hr_manager = self.env.ref('hr_holidays.group_hr_holidays_user')
        for holiday in self:
            if group_hr_manager in user.groups_id or holiday.employee_id and holiday.employee_id.user_id == user:
                holiday.can_reset = True

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        manual_att_pool = self.env["hr.manual.attendance"]
        att_pool = self.env["hr.attendance"]
        for holiday in self:
            if (holiday.date_from[:10] != holiday.date_to[:10]):
                raise ValidationError('Start Date and End Date should be same')

            domain = [
                ('date_from', '<', holiday.date_to),
                ('date_to', '>', holiday.date_from),
                ('employee_id', '=', holiday.employee_id.id),
                ('id', '!=', holiday.id),
                ('state', 'not in', ['cancel', 'refuse']),
            ]
            manual_att_domain = [
                ('check_in', '<', holiday.date_to),
                ('check_out', '>', holiday.date_from),
                ('employee_id', '=', holiday.employee_id.id),
                ('id', '!=', holiday.id),
                ('state', 'not in', ['cancel', 'refuse']),
            ]
            att_domain = [
                ('check_in', '<', holiday.date_to),
                ('check_out', '>', holiday.date_from),
                ('employee_id', '=', holiday.employee_id.id),
                ('id', '!=', holiday.id),
            ]

            nholidays = self.search_count(domain)
            if nholidays:
                raise ValidationError(_('You are trying to overlap with short leave.'
                                        'Please check your existing short leave!'))

            check_manual_att = manual_att_pool.search_count(manual_att_domain)
            if check_manual_att:
                raise ValidationError(_('You are trying to overlap with manual attendance.'
                                        'Please check your existing manual attendance!'))

            check_att = att_pool.search_count(att_domain)
            if check_att:
                raise ValidationError(_('You are trying to overlap with attendance device.'
                                        'Please check your existing attendance!'))

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

    @api.onchange('date_to')
    def _onchange_date_to(self):
        """ Update the number_of_days. """
        date_from = self.date_from
        date_to = self.date_to

        if date_from and date_to:
            if (date_from[:10] == date_to[:10]):  # only date is equal
                pass
            else:
                raise ValidationError('Start Date and End Date should be same')

    @api.multi
    def add_follower(self, employee_id):
        employee = self.env['hr.employee'].browse(employee_id)
        if employee.user_id:
            self.message_subscribe_users(user_ids=employee.user_id.ids)

    @api.multi
    def action_confirm(self):
        if self.filtered(lambda holiday: holiday.state != 'draft'):
            raise UserError(_('Leave request must be in Draft state ("To Submit") in order to confirm it.'))
        return self.write({'state': 'confirm'})

    @api.multi
    def action_approve(self):
        for short_leave in self:
            if short_leave.state != 'confirm':
                raise UserError(_('Manual Attendance Request must be confirmed ("To Approve") in order to approve it.'))
            is_last_approbation = False
            sequence = 0
            next_approver = None
            for approver in short_leave.employee_id.holidays_approvers:
                sequence = sequence + 1
                if short_leave.pending_approver.id == approver.approver.id:
                    if sequence == len(short_leave.employee_id.holidays_approvers):
                        is_last_approbation = True
                    else:
                        next_approver = short_leave.employee_id.holidays_approvers[sequence].approver
            if is_last_approbation:
                short_leave.action_validate()
            else:
                vals = {'state': 'confirm'}
                if next_approver and next_approver.id:
                    vals['pending_approver'] = next_approver.id
                short_leave.write(vals)
                self.env['hr.employee.short.leave.approbation'].create(
                    {'short_leave_ids': short_leave.id, 'approver': self.env.uid, 'sequence': sequence,
                     'date': fields.Datetime.now()})

    @api.multi
    def action_validate(self):
        if self.state == 'confirm':
            if self.holiday_status_id.half_leave_flag:
                from_dt = fields.Datetime.from_string(self.date_from)
                to_dt = fields.Datetime.from_string(self.date_to)
                time_delta = to_dt - from_dt
                vals = {
                    'leave_ids': self.id,
                    'check_hour': True,
                    'type': 'remove',
                    'holiday_status_id': self.holiday_status_id.id,
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'number_of_days_temp': (time_delta.seconds / 3600) / 8.0,
                    'employee_id': self.employee_id.id,
                    'leave_year_id': self.leave_year_id.id,
                    'state': self.state
                }
                holiday = self.env['hr.holidays'].create(vals)
                holiday.write({'state': 'validate'})
            self.write({'state': 'validate'})
            return True

    @api.multi
    def action_refuse(self):
        if not (self.env.user.has_group('hr_holidays.group_hr_holidays_user')
                or self.env.user.has_group('gbs_application_group.group_dept_manager')):
            raise UserError(_('Only an HR Officer or Manager can refuse leave requests.'))
        for holiday in self:
            if holiday.state not in ['confirm', 'validate']:
                raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))
            holiday.write({'state': 'refuse'})
        return True

    @api.multi
    def action_draft(self):
        return self.write({'state': 'draft'})

    ####################################################
    # Override methods
    ####################################################

    @api.model
    def create(self, values):
        """ Override to avoid automatic logging of creation """
        employee_id = values.get('employee_id', False)
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            if employee and employee.holidays_approvers and employee.holidays_approvers[0]:
                values['pending_approver'] = employee.holidays_approvers[0].approver.id
        holiday = super(HrShortLeave, self.with_context(mail_create_nolog=True, mail_create_nosubscribe=True)).create(
            values)
        holiday.add_follower(employee_id)
        holiday._notify_approvers()
        return holiday

    @api.multi
    def write(self, values):
        employee_id = values.get('employee_id', False)
        if employee_id:
            self.pending_approver = self.env['hr.employee'].search([('id', '=', employee_id)]).holidays_approvers[
                0].approver.id
        result = super(HrShortLeave, self).write(values)
        self.add_follower(employee_id)
        return result

    @api.multi
    def unlink(self):
        for holiday in self.filtered(lambda holiday: holiday.state not in ['draft', 'cancel', 'confirm']):
            raise UserError(_('You cannot delete a leave which is in %s state.') % (holiday.state,))
        return super(HrShortLeave, self).unlink()

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

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('draft', 'confirm'))]


class HRHolidays(models.Model):
    _inherit = 'hr.holidays'

    expire_date = fields.Date(string='Expiration Date')

    @api.constrains('holiday_type', 'type', 'employee_id', 'holiday_status_id')
    def _check_holidays(self):
        for holiday in self:
            if holiday.holiday_type != 'employee' or holiday.type != 'remove' or holiday.holiday_status_id.short_leave_flag:
                continue
            super(HRHolidays, self)._check_holidays()


class HrHolidayStatus(models.Model):
    _inherit = 'hr.holidays.status'

    short_leave_flag = fields.Boolean(string='Allow Short Leave', default=False)
    half_leave_flag = fields.Boolean(string='Allow Short Leave', default=False)
    compensatory_flag = fields.Boolean(string='Allow Compensatory Leave', default=False)
    number_of_hours = fields.Integer(string='Leave Hours')


class EmployeeLeaves(models.Model):
    _name = "hr.employee"
    _inherit = "hr.employee"

    @api.multi
    def _compute_leaves_count(self):
        super(EmployeeLeaves, self)._compute_leaves_count()

    leaves_count = fields.Float('Number of Leaves', compute='_compute_leaves_count', readonly=0)

