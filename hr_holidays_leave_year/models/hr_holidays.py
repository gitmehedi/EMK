# -*- coding: utf-8 -*-
# ©  2017 Md Mehedi Hasan <md.mehedi.info@gmail.com>

import datetime

from odoo import models, fields, api, _


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.model
    def _default_leave_year(self):
        return self.env['hr.leave.fiscal.year'].search([], limit=1)

    leave_year_id = fields.Many2one('hr.leave.fiscal.year', string="Leave Year",default=_default_leave_year)

    current_fiscal_year = fields.Boolean('Current Fiscal Year',compute='_compute_current_fiscal_year',store=True)

    # @api.depends('date_from')
    # def set_leave_year(self):
    #     if self.date_from:
    #         leave_year_pool = self.env['hr.leave.fiscal.year']
    #         leave_years = leave_year_pool.search([('date_start', '<=', self.date_from),
    #                                              ('date_stop', '>=', self.date_from)])
    #         self.leave_year_id = leave_years[0].id

    @api.multi
    @api.depends('leave_year_id')
    def _compute_current_fiscal_year(self):
        year_id = self.get_year()
        for holiday in self:
            if holiday.leave_year_id.id == year_id and holiday.holiday_status_id.active == True:
                holiday.current_fiscal_year = True
            else:
                holiday.current_fiscal_year = False

    def get_year(self):
        year_id = 0
        curr_date = datetime.date.today().strftime('%Y-%m-%d')
        self.env.cr.execute(
            "SELECT * FROM hr_leave_fiscal_year  WHERE '{}' between date_start and date_stop".format(curr_date))
        years = self.env.cr.dictfetchone()
        if years:
            year_id = years['id']
        return year_id


class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'
    
    @api.multi
    def get_days(self, employee_id):
        year_id = self.get_year()
        result = dict((id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0, virtual_remaining_leaves=0)) for id in self.ids)

        holidays = self.env['hr.holidays'].search([
            ('employee_id', '=', employee_id),
            ('state', 'in', ['confirm', 'validate1', 'validate']),
            ('holiday_status_id', 'in', self.ids)
        ])
        # year_id =1

        for holiday in holidays:
            status_dict = result[holiday.holiday_status_id.id]
            if holiday.type == 'add':
                if holiday.parent_id.leave_year_id.id == year_id or holiday.leave_year_id.id == year_id:
                    if holiday.state == 'validate':
                        # note: add only validated allocation even for the virtual
                        # count; otherwise pending then refused allocation allow
                        # the employee to create more leaves than possible
                        status_dict['virtual_remaining_leaves'] += holiday.number_of_days_temp
                        status_dict['max_leaves'] += holiday.number_of_days_temp
                        status_dict['remaining_leaves'] += holiday.number_of_days_temp
            elif holiday.type == 'remove':  # number of days is negative
                if holiday.parent_id.leave_year_id.id == year_id or holiday.leave_year_id.id == year_id:
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
