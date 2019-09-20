# -*- coding: utf-8 -*-
# ©  2016 Md Mehedi Hasan <md.mehedi.info@gmail.com>

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError,Warning
from dateutil.relativedelta import relativedelta
import math


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    # @api.model
    # def _check_date_helper(self, employee_id, date):
    #     status_id = self.holiday_status_id.id or self.env.context.get(
    #         'holiday_status_id',
    #         False)
    #     if employee_id and status_id:
    #         employee = self.env['hr.employee'].browse(employee_id)
    #         status = self.env['hr.holidays.status'].browse(status_id)
    #         if (not employee.work_scheduled_on_day(
    #                 fields.Date.from_string(date),
    #                 public_holiday=status.exclude_public_holidays,
    #                 schedule=status.exclude_rest_days)):
    #             return False
    #     return True
    #
    # @api.onchange('holiday_status_id')
    # def _onchange_holiday_status_id(self):
    #     self._check_and_recompute_days()
    #
    # def _check_and_recompute_days(self):
    #     date_from = self.date_from
    #     date_to = self.date_to
    #     if (date_to and date_from) and (date_from <= date_to):
    #         if not self._check_date_helper(self.employee_id.id, date_from):
    #             raise ValidationError(_("You cannot schedule the start date "
    #                                     "on a public holiday or employee's "
    #                                     "weekly holidays day"))
    #         if not self._check_date_helper(self.employee_id.id, date_to):
    #             raise ValidationError(_("You cannot schedule the end date "
    #                                     "on a public holiday or employee's "
    #                                     "weekly holidays day"))
    #         duration = self._compute_number_of_days(
    #             self.employee_id.id,
    #             date_to,
    #             date_from
    #         )
    #         return duration
    #
    # @api.multi
    # def onchange_employee(self, employee_id):
    #     res = super(HrHolidays, self).onchange_employee(employee_id)
    #     duration = self._check_and_recompute_days()
    #     res['value']['number_of_days_temp'] = duration
    #     return res

    @api.onchange('date_from')
    def onchange_date_from(self):
        for holiday in self:
            employee_id = holiday.employee_id.id or self.env.context.get('employee_id',False)
            holiday._onchange_date_from()
            days_check = True

            if not holiday._check_date_helper(employee_id, holiday.date_from):
                days_check = False
                diff_day = holiday._compute_number_of_days(employee_id)
                holiday.number_of_days_temp = diff_day
                raise Warning(_("You cannot schedule the start date on "
                                        "a public holiday or employee's weekly holidays day"))
                try:
                    raise Warning(_("You cannot schedule the start date on "
                                        "a public holiday or employee's weekly holidays day"))
                finally:
                    diff_day = holiday._compute_number_of_days(employee_id,date_to,date_from)
                    res['value']['number_of_days_temp'] = diff_day
                    return res

            if (holiday.date_to and holiday.date_from) and (holiday.date_from <= holiday.date_to) and days_check:
                diff_day = holiday._compute_number_of_days(employee_id,holiday.date_to,holiday.date_from)
                holiday.number_of_days_temp = diff_day

    @api.onchange('date_to')
    def onchange_date_to(self):

        res = super(HrHolidays, self)._onchange_date_to()
        employee_id = self.employee_id.id or self.env.context.get('employee_id', False)

        if not self._check_date_helper(employee_id, self.date_to):
            res['value']['number_of_days_temp'] = None
            raise ValidationError(_("You cannot schedule the end date on "
                                    "a public holiday or employee's weekly holidays day"))

        if (self.date_to and self.date_from) and (self.date_from <= self.date_to):
            diff_day = self._compute_number_of_days()
            res['value']['number_of_days_temp'] = diff_day
        return res

    @api.multi
    @api.depends('number_of_days_temp', 'type')
    def _compute_number_of_days(self):
        if not self.date_from or not self.date_to:
            return 0
        days = self._get_number_of_days(self.employee_id, self.date_from, self.date_to)
        if days or self.date_to == self.date_from:
            days = round(math.floor(days)) + 1
        status_id = self.holiday_status_id.id or self.env.context.get('holiday_status_id', False)

        if self.employee_id and self.date_from and self.date_to and status_id:
            employee = self.env['hr.employee'].browse(self.employee_id)
            status = self.env['hr.holidays.status'].browse(status_id)
            date_from = fields.Date.from_string(self.date_from)
            date_to = fields.Date.from_string(self.date_to)
            date_dt = date_from
            while date_dt <= date_to:
                # if public holiday or rest day let us skip
                if not employee.work_scheduled_on_day(
                        date_dt,
                        status.exclude_public_holidays,
                        status.exclude_rest_days
                ):
                    days -= 1
                date_dt += relativedelta(days=1)
        return days
