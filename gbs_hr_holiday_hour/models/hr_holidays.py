# -*- coding: utf-8 -*-

from odoo import models, fields, api,SUPERUSER_ID
from odoo.exceptions import UserError, AccessError, ValidationError

HOURS_PER_DAY = 8


class HrHolidayHour(models.Model):
    _name = 'hr.holiday.hour'
    _inherit = 'hr.holidays'

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)


    leave_year_id = fields.Many2one('date.range', string="Leave Year",
                                    domain="[('type_id.holiday_year', '=', True)]")

    name = fields.Char('Description')
    employee_id = fields.Many2one('hr.employee', string='Employee', index=True, readonly=True,required=True,
                                  states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, default=_default_employee)
    date_from = fields.Datetime('Start Time', readonly=True, index=True, copy=False, required=True,
                                track_visibility='onchange',
                                states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    date_to = fields.Datetime('End Time', readonly=True, copy=False, required=True, track_visibility='onchange',
                              states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    number_of_days = fields.Float('Number of Days', compute='_compute_total_hours', readonly=True, store=True)
    holiday_status_id = fields.Many2one("hr.holidays.status", string="Leave Type", required=True, readonly=True,
                                        domain="[('short_leave_flag','=',True)]",
                                        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    check_hour = fields.Boolean(string='Half Leave', default=True)

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

    # @api.multi
    # def action_confirm(self):
    #     if self.filtered(lambda holiday: holiday.state != 'draft'):
    #         raise UserError(_('Leave request must be in Draft state ("To Submit") in order to confirm it.'))
    #     return self.write({'state': 'confirm'})
    #
    # @api.multi
    # def action_approve(self):
    #     return self.write({'state': 'confirm'})


    @api.multi
    def action_validate(self):
        from_dt = fields.Datetime.from_string(self.date_from)
        to_dt = fields.Datetime.from_string(self.date_to)
        time_delta = to_dt - from_dt
        self.write({'state': 'validate'})
        self.env['hr.holidays'].create(
            {'leave_ids': self.id,
             'check_hour':True,
             'type': 'remove',
             'holiday_status_id': self.holiday_status_id.id,
             'date_from': self.date_from,
             'date_to': self.date_to,
             'number_of_days_temp': (time_delta.seconds / 3600) / 8.0,
             'employee_id': self.employee_id.id,
             'leave_year_id': self.leave_year_id.id,
             'state':self.state
             })

        self.write({'state': 'validate'})
        return True

    # @api.multi
    # def action_refuse(self):
    #     return self.write({'state': 'refuse'})
    #
    @api.multi
    def action_draft1(self):
        return self.write({'state': 'draft'})

    @api.constrains('number_of_days')
    def _check_number_of_days(self):
        if self.holiday_status_id.compensatory_flag == False:
            if self.holiday_status_id.short_leave_flag and self.number_of_days:
               if self.number_of_days != 4.00 :
                   raise ValidationError('Half day leave takes only 4 hours!')
               else:
                   pass

    @api.constrains('date_to')
    def _compute_date(self):

        date_from = self.date_from
        date_to = self.date_to
        holidays = self.env['hr.holidays'].search([])
        for i in holidays:
            if i.expire_date:
                if date_from > i.expire_date or date_to > i.expire_date:
                    raise ValidationError('Your Allocation date is expired!!')
                else:
                    pass


class HrHolidayStatus(models.Model):
    _inherit = 'hr.holidays.status'

    short_leave_flag = fields.Boolean(string='Allow Short Leave', default=False)
    compensatory_flag = fields.Boolean(string='Allow Compensatory Leave', default=False)

class EmployeeLeaves(models.Model):
    _name = "hr.employee"
    _inherit = "hr.employee"

    @api.multi
    def _compute_leaves_count(self):
        super(EmployeeLeaves, self)._compute_leaves_count()

    leaves_count = fields.Float('Number of Leaves', compute='_compute_leaves_count',readonly=0)


class HrHoliday(models.Model):
    _inherit = 'hr.holidays'

    expire_date = fields.Date(string='Expiration Date')