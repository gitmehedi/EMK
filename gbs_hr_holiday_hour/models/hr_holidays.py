# -*- coding: utf-8 -*-

from odoo import models, fields, api,SUPERUSER_ID
import logging
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.translate import _

HOURS_PER_DAY = 8


class HrHolidayHour(models.Model):
    _name = 'hr.holiday.hour'
    _inherit = 'hr.holidays'

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)


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

    @api.multi
    def action_confirm(self):
        if self.filtered(lambda holiday: holiday.state != 'draft'):
            raise UserError(_('Leave request must be in Draft state ("To Submit") in order to confirm it.'))
        return self.write({'state': 'confirm'})

    @api.multi
    def action_approve(self):
        return self.write({'state': 'confirm'})


    @api.multi
    def action_validate(self):
        from_dt = fields.Datetime.from_string(self.date_from)
        to_dt = fields.Datetime.from_string(self.date_to)
        time_delta = to_dt - from_dt
        self.env['hr.holidays'].create(
            {'leave_ids': self.id,
             'check_hour':True,
             'type': 'remove',
             'holiday_status_id': self.holiday_status_id.id,
             'date_from': self.date_from,
             'date_to': self.date_to,
             'number_of_days_temp': (time_delta.seconds / 3600) / 8.0,
             'employee_id': self.employee_id.id,
             })

        self.write({'state': 'validate'})
        return True

    @api.multi
    def action_refuse(self):
        return self.write({'state': 'refuse'})

    @api.multi
    def action_draft(self):
        return self.write({'state': 'draft'})


class HrShortLeave(models.Model):
    _inherit = 'hr.holidays.status'

    short_leave_flag = fields.Boolean(string='Allow Short Leave', default=False)


# class HRHolidays(models.Model):
#     _inherit = 'hr.holidays'
#
#     @api.model
#     def create(self, values):
#         res = super(HRHolidays, self).create(values)
#         time_delta = (fields.Datetime.from_string(values['date_to']) - fields.Datetime.from_string(values['date_from']))
#         time = ((time_delta.seconds / 3600) / 8.0)
#         res['number_of_days_temp'] = time
#         return res