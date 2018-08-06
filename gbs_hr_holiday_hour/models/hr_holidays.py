# -*- coding: utf-8 -*-

import datetime
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
import math
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, Warning

HOURS_PER_DAY = 8


class HrHolidayHour(models.Model):
    _name = 'hr.holiday.hour'
    _inherit = 'hr.holidays'

    date_from = fields.Datetime('Start Date', readonly=True, index=True, copy=False,
                                states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    date_to = fields.Datetime('End Date', readonly=True, copy=False,
                              states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})

    number_of_hours_temp = fields.Float(string='Allocation in Hours',digits=(2, 2),readonly=True,
        states={'draft': [('readonly', False)],
                'confirm': [('readonly', False)]}
    )
    number_of_hours = fields.Float(
        compute='_compute_number_of_hours',
        store=True
    )

    @api.depends('number_of_hours_temp', 'state')
    def _compute_number_of_hours(self):
        for rec in self:
            number_of_hours = rec.number_of_hours_temp
            if rec.type == 'remove':
                number_of_hours = -rec.number_of_hours_temp

            rec.virtual_hours = number_of_hours
            if rec.state not in ('validate',):
                number_of_hours = 0.0
            rec.number_of_hours = number_of_hours

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
        time_delta = to_dt - from_dt
        return math.ceil(time_delta.days + float(time_delta.seconds) / 3600)
        #return math.ceil(time_delta.days + float(time_delta.seconds) / 86400)

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
            self.number_of_hours_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
        else:
            self.number_of_hours_temp = 0

    @api.multi
    def _check_dates(self):
        self.ensure_one()
        # date_to has to be greater than date_from
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise Warning(_(
                    'The start date must be anterior to the end date.'
                ))

    @api.multi
    def _check_employee(self):
        self.ensure_one()
        employee = self.employee_id
        if not employee and (self.date_to or self.date_from):
            raise Warning(_('Set an employee first!'))