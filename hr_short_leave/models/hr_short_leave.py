from odoo import models, fields, api
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
    _order = "type desc, date_from desc"
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
    payslip_status = fields.Boolean('Reported in last payslips',
        help='Green this button when the leave has been taken into account in the payslip.')
    report_note = fields.Text('HR Comments')
    user_id = fields.Many2one('res.users', string='User', related='employee_id.user_id', related_sudo=True, store=True, default=lambda self: self.env.uid, readonly=True)
    date_from = fields.Datetime('Start Time', readonly=True, index=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    date_to = fields.Datetime('End Time', readonly=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string='Employee', index=True, readonly=True,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, default=_default_employee)
    manager_id = fields.Many2one('hr.employee', string='First Approval', readonly=True, copy=False,
        help='This area is automatically filled by the user who validate the leave')
    notes = fields.Text('Reasons', readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    number_of_days_temp = fields.Float('Allocation', readonly=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    number_of_days = fields.Float('Number of Days', compute='_compute_number_of_days', store=True)
    meeting_id = fields.Many2one('calendar.event', string='Meeting')
    type = fields.Selection([
            ('remove', 'Leave Request'),
            ('add', 'Allocation Request')
        ], string='Request Type', required=True, readonly=True, index=True, default='remove',
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
        help="Choose 'Leave Request' if someone wants to take an off-day. "
             "\nChoose 'Allocation Request' if you want to increase the number of leaves available for someone")
    parent_id = fields.Many2one('hr.holidays', string='Parent')
    linked_request_ids = fields.One2many('hr.holidays', 'parent_id', string='Linked Requests')
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department', readonly=True, store=True)
    category_id = fields.Many2one('hr.employee.category', string='Employee Tag', readonly=True,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, help='Category of Employee')
    holiday_type = fields.Selection([
        ('employee', 'By Employee'),
        ('category', 'By Employee Tag')
    ], string='Allocation Mode', readonly=True, required=True, default='employee',
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
        help='By Employee: Allocation/Request for individual Employee, By Employee Tag: Allocation/Request for group of employees in category')
    manager_id2 = fields.Many2one('hr.employee', string='Second Approval', readonly=True, copy=False,
        help='This area is automaticly filled by the user who validate the leave with second level (If Leave type need second validation)')
    double_validation = fields.Boolean('Apply Double Validation', default=True)
    can_reset = fields.Boolean('Can reset', compute='_compute_can_reset')

    @api.multi
    @api.depends('number_of_days_temp', 'type')
    def _compute_number_of_days(self):
        for holiday in self:
            if holiday.type == 'remove':
                holiday.number_of_days = -holiday.number_of_days_temp
            else:
                holiday.number_of_days = holiday.number_of_days_temp

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
                ('type', '=', holiday.type),
                ('state', 'not in', ['cancel', 'refuse']),
            ]
            nholidays = self.search_count(domain)
            if nholidays:
                raise ValidationError(_('You can not have 2 leaves that overlaps on same day!'))

    _sql_constraints = [
        ('type_value', "CHECK( (holiday_type='employee' AND employee_id IS NOT NULL) or (holiday_type='category' AND category_id IS NOT NULL))",
         "The employee or employee category of this request is missing. Please make sure that your user login is linked to an employee."),
        ('date_check2', "CHECK ( (type='add') OR (date_from <= date_to))", "The start date must be anterior to the end date."),
        ('date_check', "CHECK ( number_of_days_temp >= 0 )", "The number of days must be greater than 0."),
    ]

    @api.onchange('holiday_type')
    def _onchange_type(self):
        if self.holiday_type == 'employee' and not self.employee_id:
            self.employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        elif self.holiday_type != 'employee':
            self.employee_id = None

    @api.onchange('employee_id')
    def _onchange_employee(self):
        self.department_id = self.employee_id.department_id

    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        from_dt = fields.Datetime.from_string(date_from)
        to_dt = fields.Datetime.from_string(date_to)

        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            resource = employee.resource_id.sudo()
            if resource and resource.calendar_id:
                hours = resource.calendar_id.get_working_hours(from_dt, to_dt, resource_id=resource.id, compute_leaves=True)
                uom_hour = resource.calendar_id.uom_id
                uom_day = self.env.ref('product.product_uom_day')
                if uom_hour and uom_day:
                    return uom_hour._compute_quantity(hours, uom_day)

        time_delta = to_dt - from_dt
        return time_delta.days + (float(time_delta.seconds) / 3600)  #Take only Time difference

    @api.onchange('date_from')
    def _onchange_date_from(self):
        """ If there are no date set for date_to, automatically set one 8 hours later than
            the date_from. Also update the number_of_days.
        """
        date_from = self.date_from
        date_to = self.date_to

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_to_with_delta = fields.Datetime.from_string(date_from) #+ timedelta(hours=HOURS_PER_DAY)
            self.date_to = str(date_to_with_delta)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
        else:
            self.number_of_days_temp = 0

    @api.onchange('date_to')
    def _onchange_date_to(self):
        """ Update the number_of_days. """
        date_from = self.date_from
        date_to = self.date_to

        if date_from and date_to:
            if (date_from[:10] == date_to[:10]):  # only date is equal
                # Compute and update the number of days
                if (date_to and date_from) and (date_from <= date_to):
                    self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
                else:
                    self.number_of_days_temp = 0
            else:
                raise ValidationError('Start Date and End Date should be same')

    @api.multi
    def name_get(self):
        res = []

        for leave in self:
            computed_hours = leave.number_of_days_temp
            res.append((leave.id, _("%s on %s : %.2f hour(s)") % (leave.employee_id.name or leave.category_id.name, ' Short Leave', computed_hours)))
        return res

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
        return holiday

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

    ####################################################
    # Business methods
    ####################################################

    @api.multi
    def _create_resource_leave(self):
        """ This method will create entry in resource calendar leave object at the time of holidays validated """
        for leave in self:
            self.env['resource.calendar.leaves'].create({
                'name': leave.name,
                'date_from': leave.date_from,
                'holiday_id': leave.id,
                'date_to': leave.date_to,
                'resource_id': leave.employee_id.resource_id.id,
                'calendar_id': leave.employee_id.resource_id.calendar_id.id
            })
        return True

    @api.multi
    def _remove_resource_leave(self):
        """ This method will create entry in resource calendar leave object at the time of holidays cancel/removed """
        return self.env['resource.calendar.leaves'].search([('holiday_id', 'in', self.ids)]).unlink()

    @api.multi
    def action_draft(self):
        for holiday in self:
            if not holiday.can_reset:
                raise UserError(_('Only an HR Manager or the concerned employee can reset to draft.'))
            if holiday.state not in ['confirm', 'refuse']:
                raise UserError(_('Leave request state must be "Refused" or "To Approve" in order to reset to Draft.'))
            holiday.write({
                'state': 'draft',
                'manager_id': False,
                'manager_id2': False,
            })
            linked_requests = holiday.mapped('linked_request_ids')
            for linked_request in linked_requests:
                linked_request.action_draft()
            linked_requests.unlink()
        return True

    @api.multi
    def action_confirm(self):
        if self.filtered(lambda holiday: holiday.state != 'draft'):
            raise UserError(_('Leave request must be in Draft state ("To Submit") in order to confirm it.'))
        return self.write({'state': 'confirm'})

    @api.multi
    def action_approve(self):
        # if double_validation: this method is the first approval approval
        # if not double_validation: this method calls action_validate() below
        if not (self.env.user.has_group('hr_holidays.group_hr_holidays_user') or self.env.user.has_group('gbs_base_package.group_dept_manager')):
            raise UserError(_('Only Department Manager can approve leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state != 'confirm':
                raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))

            if holiday.double_validation:
                 return holiday.write({'state': 'validate1', 'manager_id': manager.id if manager else False})
            else:
                 holiday.action_validate()

    @api.multi
    def action_validate(self):
        if not (self.env.user.has_group('hr_holidays.group_hr_holidays_user') or self.env.user.has_group('gbs_base_package.group_dept_manager')):
            raise UserError(_('Only an HR Officer or Manager or Department Manager can approve leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate1']:
                raise UserError(_('Leave request must be confirmed in order to approve it.'))
            if holiday.state == 'validate1' and not holiday.env.user.has_group('hr_holidays.group_hr_holidays_user'):
                raise UserError(_('Only an HR Manager can apply the second approval on leave requests.'))

            holiday.write({'state': 'validate'})
            if holiday.double_validation:
                holiday.write({'manager_id2': manager.id})
            else:
                holiday.write({'manager_id': manager.id})
            if holiday.holiday_type == 'employee' and holiday.type == 'remove':
                meeting_values = {
                    'name': holiday.display_name,
                    #'categ_ids': [(6, 0, [holiday.holiday_status_id.categ_id.id])] if holiday.holiday_status_id.categ_id else [],
                    'duration': holiday.number_of_days_temp * HOURS_PER_DAY,
                    'description': holiday.notes,
                    'user_id': holiday.user_id.id,
                    'start': holiday.date_from,
                    'stop': holiday.date_to,
                    'allday': False,
                    'state': 'open',            # to block that meeting date in the calendar
                    'privacy': 'confidential'
                }
                #Add the partner_id (if exist) as an attendee
                if holiday.user_id and holiday.user_id.partner_id:
                    meeting_values['partner_ids'] = [(4, holiday.user_id.partner_id.id)]

                meeting = self.env['calendar.event'].with_context(no_mail_to_attendees=True).create(meeting_values)
                holiday.write({'meeting_id': meeting.id})

        return True

    @api.multi
    def action_refuse(self):
        if not (self.env.user.has_group('hr_holidays.group_hr_holidays_user')
                or self.env.user.has_group('gbs_base_package.group_dept_manager')):
            raise UserError(_('Only an HR Officer or Manager can refuse leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate', 'validate1']:
                raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))

            if holiday.state == 'validate1':
                holiday.write({'state': 'refuse', 'manager_id': manager.id})
            else:
                holiday.write({'state': 'refuse', 'manager_id2': manager.id})
            # Delete the meeting
            if holiday.meeting_id:
                holiday.meeting_id.unlink()
            # If a category that created several holidays, cancel all related
            holiday.linked_request_ids.action_refuse()
        self._remove_resource_leave()
        return True

    @api.multi
    def toggle_payslip_status(self):
        record_to_set_true = self.search([('id', 'in', self.ids), ('payslip_status', '=', False)])
        record_to_set_false = self - record_to_set_true
        return record_to_set_true.write({'payslip_status': True}) and record_to_set_false.write({'payslip_status': False})

    ####################################################
    # Messaging methods
    ####################################################

    @api.multi
    def _track_subtype(self, init_values):
        if 'state' in init_values and self.state == 'validate':
            return 'hr_holidays.mt_holidays_approved'
        elif 'state' in init_values and self.state == 'validate1':
            return 'hr_holidays.mt_holidays_first_validated'
        elif 'state' in init_values and self.state == 'confirm':
            return 'hr_holidays.mt_holidays_confirmed'
        elif 'state' in init_values and self.state == 'refuse':
            return 'hr_holidays.mt_holidays_refused'
        return super(HrShortLeave, self)._track_subtype(init_values)

    @api.multi
    def _notification_recipients(self, message, groups):
        """ Handle HR users and officers recipients that can validate or refuse holidays
        directly from email. """
        groups = super(HrShortLeave, self)._notification_recipients(message, groups)

        self.ensure_one()
        hr_actions = []
        if self.state == 'confirm':
            app_action = self._notification_link_helper('controller', controller='/hr_holidays/validate')
            hr_actions += [{'url': app_action, 'title': _('Approve')}]
        if self.state in ['confirm', 'validate', 'validate1']:
            ref_action = self._notification_link_helper('controller', controller='/hr_holidays/refuse')
            hr_actions += [{'url': ref_action, 'title': _('Refuse')}]

        new_group = (
            'group_hr_holidays_user', lambda partner: bool(partner.user_ids) and any(user.has_group('hr_holidays.group_hr_holidays_user') for user in partner.user_ids), {
                'actions': hr_actions,
            })

        return [new_group] + groups
