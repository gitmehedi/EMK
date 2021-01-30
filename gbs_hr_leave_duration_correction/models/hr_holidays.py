from odoo import fields, models, api
from datetime import date
from datetime import datetime
import math
from datetime import timedelta
from odoo.exceptions import UserError, AccessError, ValidationError

HOURS_PER_DAY = 8

class HRHolidays(models.Model):
    _inherit = 'hr.holidays'

    def _current_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    date_from = fields.Date('Start Date', readonly=True, index=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    date_to = fields.Date('End Date', readonly=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})

    number_of_days_temp = fields.Float('Allocation', readonly=True, copy=False,
                        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})

    number_of_days = fields.Float('Number of Days', compute='_compute_number_of_days', store=True)

    ## Newly Introduced Fields
    requested_by = fields.Many2one('hr.employee', string="Requisition By", default=_current_employee, readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', index=True, readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
                            default=_default_employee)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department', readonly=True, store=True)
    check_hour = fields.Boolean(string='Half Leave',default= False)

    @api.model
    def create(self, values):
        if (values.get('type') == 'remove'
            and values.get('date_from') is not False and values.get('check_hour') is not True
            and values.get('date_to') is not False):
            date_from = values.get('date_from')
            date_to = values.get('date_to')
            d1 = fields.Datetime.from_string(date_from)
            d2 = fields.Datetime.from_string(date_to)
            duration = (d2 - d1).days + 1
            values['number_of_days_temp'] = duration
        return super(HRHolidays, self).create(values)

    @api.multi
    def write(self, values):
        # if values.get('check_hour') is False:
            for holiday in self:
                if (holiday.type == 'remove'):
                    start_date = holiday.date_from
                    end_date = holiday.date_to

                    if (values.get('date_from', False) != False):
                        start_date = values.get('date_from')

                    if (values.get('date_to', False) != False):
                        end_date = values.get('date_to')

                    d1 = fields.Datetime.from_string(start_date)
                    d2 = fields.Datetime.from_string(end_date)

                    duration = (d2 - d1).days + 1
                    values['number_of_days_temp'] = duration
            return super(HRHolidays, self).write(values)
        # else:
        #     return super(HRHolidays, self).write(values)

    """
       As we removed Datetime data type so we have added 1d with date difference
    """
    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        from_dt = fields.Datetime.from_string(date_from)
        to_dt = fields.Datetime.from_string(date_to)

        # if employee_id:
        #     employee = self.env['hr.employee'].browse(employee_id)
        #     resource = employee.resource_id.sudo()
        #     if resource and resource.calendar_id:
        #         hours = resource.calendar_id.get_working_hours(from_dt, to_dt, resource_id=resource.id,
        #                                                        compute_leaves=True)
        #         uom_hour = resource.calendar_id.uom_id
        #         uom_day = self.env.ref('product.product_uom_day')
        #         if uom_hour and uom_day:
        #             return uom_hour._compute_quantity(hours, uom_day)

        time_delta = (to_dt - from_dt) + timedelta(hours=24)
        return math.ceil(time_delta.days + float(time_delta.seconds) / 86400)


    @api.onchange('date_from')
    def _onchange_date_from(self):
        """ If there are no date set for date_to, automatically set one 8 hours later than
            the date_from. Also update the number_of_days.
        """
        date_from = self.date_from
        date_to = self.date_to

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_to_with_delta = fields.Datetime.from_string(date_from) + timedelta(hours=HOURS_PER_DAY)
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

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
        else:
            self.number_of_days_temp = 0

    @api.multi
    def action_approve(self):
        # if double_validation: this method is the first approval approval
        # if not double_validation: this method calls action_validate() below
        if not (self.env.user.has_group('hr_holidays.group_hr_holidays_user')
                or self.env.user.has_group('gbs_application_group.group_dept_manager')):
            raise ValidationError(('Only an HR Officer or Manager or Department Manager can approve leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if not holiday.parent_id and holiday.state != 'confirm':
                raise ValidationError(('Leave request must be confirmed ("To Approve") in order to approve it.'))

            if holiday.double_validation:
                return holiday.write({'state': 'validate1', 'manager_id': manager.id if manager else False})
            else:
                holiday.action_validate()

    @api.multi
    def action_validate(self):
        if not (self.env.user.has_group('hr_holidays.group_hr_holidays_user')):
            raise UserError(('Only an HR Officer or Manager or Department Manager can approve leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if not holiday.parent_id and holiday.state not in ['confirm', 'validate1']:
                raise ValidationError(('Leave request must be confirmed in order to approve it.'))
            if holiday.state == 'validate1' and not ((holiday.env.user.has_group('hr_holidays.group_hr_holidays_user')
                                                     or holiday.env.user.has_group('gbs_application_group.group_dept_manager'))):
                raise ValidationError(('Only an HR Manager can apply the second approval on leave requests.'))

            holiday.write({'state': 'validate'})
            if holiday.double_validation:
                holiday.write({'manager_id2': manager.id})
            else:
                holiday.write({'manager_id': manager.id})
            if holiday.holiday_type == 'employee' and holiday.type == 'remove':
                meeting_values = {
                    'name': holiday.display_name,
                    'categ_ids': [
                        (6, 0, [holiday.holiday_status_id.categ_id.id])] if holiday.holiday_status_id.categ_id else [],
                    'duration': holiday.number_of_days_temp * HOURS_PER_DAY,
                    'description': holiday.notes,
                    'user_id': holiday.user_id.id,
                    'start': holiday.date_from,
                    'stop': holiday.date_to,
                    'allday': False,
                    'state': 'open',  # to block that meeting date in the calendar
                    'privacy': 'confidential'
                }
                # Add the partner_id (if exist) as an attendee
                if holiday.user_id and holiday.user_id.partner_id:
                    meeting_values['partner_ids'] = [(4, holiday.user_id.partner_id.id)]

                meeting = self.env['calendar.event'].with_context(no_mail_to_attendees=True).create(meeting_values)
                holiday._create_resource_leave()
                holiday.write({'meeting_id': meeting.id})
            elif holiday.holiday_type == 'category':
                leaves = self.env['hr.holidays']
                for employee in holiday.category_id.employee_ids:
                    values = holiday._prepare_create_by_category(employee)
                    leaves += self.with_context(mail_notify_force_send=False).create(values)
                # TODO is it necessary to interleave the calls?
                leaves.action_approve()
                if leaves and leaves[0].double_validation:
                    leaves.action_validate()
        return True

    # def _check_state_access_right(self, vals):
    #     if vals.get('state') and vals['state'] not in ['draft', 'confirm', 'cancel'] and not (self.env['res.users'].has_group('hr_holidays.group_hr_holidays_user')):
    #         return False
    #     return True
