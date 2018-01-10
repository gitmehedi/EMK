# -*- coding: utf-8 -*-
# ©  2017 Md Mehedi Hasan <md.mehedi.info@gmail.com>

import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    leave_year_id = fields.Many2one('hr.leave.fiscal.year', string="Leave Year")

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        for holiday in self:
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
            elif holiday.type == 'remove':
                if holiday.date_from >= holiday.leave_year_id.date_start and holiday.date_to <= holiday.leave_year_id.date_stop:
                    pass
                else:
                    raise ValidationError(_('Leave duration starting date and ending date should be same year!!'))

    @api.onchange('date_from')
    def onchange_date_from(self):
        year_id = 0
        if self.date_from:
            res_date = self.date_from
        else:
            res_date = datetime.date.today().strftime('%Y-%m-%d')

        self.env.cr.execute(
            "SELECT * FROM hr_leave_fiscal_year  WHERE '{}' between date_start and date_stop".format(res_date))
        years = self.env.cr.dictfetchone()

        if not years:
            raise ValidationError(_('Unable to apply leave request. Please contract your administrator.'))

        year_id = years['id']

        self.leave_year_id = year_id

    @api.multi
    def _prepare_create_by_category(self,employee):
        values = super(HrHolidays, self)._prepare_create_by_category(employee)
        values['leave_year_id'] = self.leave_year_id.id
        return values


class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'

    @api.multi
    def get_days(self, employee_id):
        year_id = self.get_year()
        result = dict(
            (id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0, virtual_remaining_leaves=0)) for id in self.ids)

        holidays = self.env['hr.holidays'].search([
            ('employee_id', '=', employee_id),
            ('state', 'in', ['confirm', 'validate1', 'validate']),
            ('holiday_status_id', 'in', self.ids),
            ('leave_year_id', '=', year_id)
        ])

        for holiday in holidays:
            status_dict = result[holiday.holiday_status_id.id]
            if holiday.type == 'add':
                if holiday.state == 'validate':
                    # note: add only validated allocation even for the virtual
                    # count; otherwise pending then refused allocation allow
                    # the employee to create more leaves than possible
                    status_dict['virtual_remaining_leaves'] += holiday.number_of_days_temp
                    status_dict['max_leaves'] += holiday.number_of_days_temp
                    status_dict['remaining_leaves'] += holiday.number_of_days_temp
            elif holiday.type == 'remove':  # number of days is negative
                status_dict['virtual_remaining_leaves'] -= holiday.number_of_days_temp
                if holiday.state == 'validate':
                    status_dict['leaves_taken'] += holiday.number_of_days_temp
                    status_dict['remaining_leaves'] -= holiday.number_of_days_temp
        return result

    def get_year(self):
        year_id = 0
        curr_date = datetime.date.today().strftime('%Y-%m-%d')
        self.env.cr.execute(
            "SELECT * FROM hr_leave_fiscal_year  WHERE '{}' between date_start and date_stop".format(curr_date))
        years = self.env.cr.dictfetchone()
        if years:
            year_id = years['id']
        return year_id
