from odoo import models, fields, api,SUPERUSER_ID
import datetime
from datetime import datetime
from datetime import timedelta

import logging
import math
from datetime import timedelta
from werkzeug import url_encode

from odoo.exceptions import UserError, AccessError, ValidationError
from openerp.tools import float_compare
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


HOURS_PER_DAY = 8


class HrShortLeave(models.Model):

    _name = "hr.short.leave"
    _description = "Short Leaves "
    _order = "date_from desc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    name = fields.Char('Description')
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
        ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='confirm',
            help="The status is set to 'To Submit', when a holiday request is created." +
            "\nThe status is 'To Approve', when holiday request is confirmed by user." +
            "\nThe status is 'Refused', when holiday request is refused by manager." +
            "\nThe status is 'Approved', when holiday request is approved by manager.")
    report_note = fields.Text('HR Comments')
    user_id = fields.Many2one('res.users', string='User', related='employee_id.user_id', related_sudo=True, store=True, default=lambda self: self.env.uid, readonly=True)
    date_from = fields.Datetime('Start Time', readonly=True, index=True, copy=False,required=True,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    date_to = fields.Datetime('End Time', readonly=True, copy=False,required=True,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string='Employee', index=True, readonly=True,required=True,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, default=_default_employee)
    notes = fields.Text('Reasons', readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    number_of_days = fields.Float('Number of Days', compute='_compute_total_hours', readonly=True, store=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department', readonly=True, store=True)
    can_reset = fields.Boolean('Can reset', compute='_compute_can_reset')

    first_approval = fields.Boolean('First Approval', compute='compute_check_first_approval')


    @api.depends('date_from', 'date_to')
    def _compute_total_hours(self):
        if self.date_from and self.date_to:
            start_dt = fields.Datetime.from_string(self.date_from)
            finish_dt = fields.Datetime.from_string(self.date_to)
            diff = finish_dt - start_dt
            hours = float(diff.total_seconds() / 3600)
            self.number_of_days = hours

    @api.multi
    def _compute_can_reset(self):
        """ User can reset a leave request if it is its own leave request
            or if he is an Hr Manager.
        """
        user = self.env.user
        group_hr_manager = self.env.ref('hr_holidays.group_hr_holidays_manager')
        for holiday in self:
            if group_hr_manager in user.groups_id or holiday.employee_id and holiday.employee_id.user_id == user:
                holiday.can_reset = True

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        for holiday in self:
            if (holiday.date_from[:10] != holiday.date_to[:10]):
                raise ValidationError('Start Date and End Date should be same')

            domain = [
                ('date_from', '<=', holiday.date_to),
                ('date_to', '>=', holiday.date_from),
                ('employee_id', '=', holiday.employee_id.id),
                ('id', '!=', holiday.id),
                ('state', 'not in', ['cancel', 'refuse']),
            ]
            nholidays = self.search_count(domain)
            if nholidays:
                raise ValidationError(_('You can not have 2 leaves that overlaps on same day!'))

    _sql_constraints = [
        ('date_check2', "CHECK ( (date_from <= date_to))", "The start date must be anterior to the end date."),
        ('date_check', "CHECK ( number_of_days >= 0 )", "The number of days must be greater than 0."),
    ]

    @api.onchange('employee_id')
    def _onchange_employee(self):
        self.department_id = self.employee_id.department_id

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
    def _check_state_access_right(self, vals):
        if vals.get('state') and vals['state'] not in ['draft', 'confirm', 'cancel'] and not (
            self.env['res.users'].has_group('hr_holidays.group_hr_holidays_user')
        or self.env['res.users'].has_group('gbs_base_package.group_dept_manager')):
            return False
        return True

    @api.multi
    def add_follower(self, employee_id):
        employee = self.env['hr.employee'].browse(employee_id)
        if employee.user_id:
            self.message_subscribe_users(user_ids=employee.user_id.ids)

    @api.model
    def create(self, values):
        """ Override to avoid automatic logging of creation """
        employee_id = values.get('employee_id', False)
        if not self._check_state_access_right(values):
            raise AccessError(_('You cannot set a leave request as \'%s\'. Contact a human resource manager.') % values.get('state'))
        if not values.get('department_id'):
            values.update({'department_id': self.env['hr.employee'].browse(employee_id).department_id.id})
        holiday = super(HrShortLeave, self.with_context(mail_create_nolog=True, mail_create_nosubscribe=True)).create(values)
        holiday.add_follower(employee_id)
        holiday._notify_approvers()
        return holiday

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
    def write(self, values):
        employee_id = values.get('employee_id', False)
        if not self._check_state_access_right(values):
            raise AccessError(_('You cannot set a leave request as \'%s\'. Contact a human resource manager.') % values.get('state'))
        result = super(HrShortLeave, self).write(values)
        self.add_follower(employee_id)
        return result

    @api.multi
    def unlink(self):
        for holiday in self.filtered(lambda holiday: holiday.state not in ['draft', 'cancel', 'confirm']):
            raise UserError(_('You cannot delete a leave which is in %s state.') % (holiday.state,))
        return super(HrShortLeave, self).unlink()

    @api.multi
    def action_draft(self):
        return self.write({'state': 'draft'})

    @api.multi
    def action_confirm(self):
        if self.filtered(lambda holiday: holiday.state != 'draft'):
            raise UserError(_('Leave request must be in Draft state ("To Submit") in order to confirm it.'))
        return self.write({'state': 'confirm'})

    @api.multi
    def action_approve(self):
        return self.write({'state': 'validate1'})

    @api.multi
    def action_validate(self):
        if not (self.env.user.has_group('hr_holidays.group_hr_holidays_user') or self.env.user.has_group('gbs_base_package.group_dept_manager')):
            raise UserError(_('Only an HR Officer or Manager or Department Manager can approve leave requests.'))

        attendance_obj = self.env['hr.attendance']
        for holiday in self:
            if holiday.state not in ['confirm', 'validate1']:
                raise UserError(_('Leave request must be confirmed in order to approve it.'))
            if holiday.state == 'validate1' and not holiday.env.user.has_group('hr_holidays.group_hr_holidays_user'):
                raise UserError(_('Only an HR Manager can apply the second approval on leave requests.'))
            vals1 = {}
            vals1['employee_id'] = holiday.employee_id.id
            vals1['operating_unit_id'] = holiday.employee_id.operating_unit_id.id
            vals1['manual_attendance_request'] = False
            vals1['is_system_generated'] = False
            vals1['has_error'] = False
            vals1['is_short_leave'] = True
            vals1['check_in'] = holiday.date_from
            vals1['check_out'] = holiday.date_to
            attendance_obj.create(vals1)

            holiday.write({'state': 'validate'})

            return True


    @api.multi
    def action_refuse(self):
        if not (self.env.user.has_group('hr_holidays.group_hr_holidays_user')
                or self.env.user.has_group('gbs_base_package.group_dept_manager')):
            raise UserError(_('Only an HR Officer or Manager can refuse leave requests.'))
        for holiday in self:
            if holiday.state not in ['confirm', 'validate', 'validate1']:
                raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))
            holiday.write({'state': 'refuse'})
        return True

    ### User and state wise approve button hide function
    @api.multi
    def compute_check_first_approval(self):
        for h in self:
            if h.state != 'confirm':
                h.first_approval = False
            ### no one can approve own request
            elif h.employee_id.user_id.id == self.env.user.id:
                h.first_approval = False
            else:
                res = h.employee_id.check_1st_level_approval()
                h.first_approval = res


class HrEmployee(models.Model):
    _inherit = "hr.attendance"

    is_short_leave = fields.Boolean(string='Is Short Leave', default=False)