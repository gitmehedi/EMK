# -*- coding: utf-8 -*-
# ©  2016 Md Mehedi Hasan <md.mehedi.info@gmail.com>

import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,Warning


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    
    leave_year_id = fields.Many2one('hr.leave.fiscal.year', string="Leave Year", required=True)
    
    
    
class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'
    
    @api.multi
    def get_days(self, employee_id):
        # need to use `dict` constructor to create a dict per id
        now = datetime.datetime.now()
        print now.year, now.month, now.day, now.hour, now.minute, now.secon
#         year_id = self.env['hr.leave.fiscal_year'].search([('date_start')])
        
        result = dict((id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0, virtual_remaining_leaves=0)) for id in self.ids)


        holidays = self.env['hr.holidays'].search([
            ('employee_id', '=', employee_id),
            ('state', 'in', ['confirm', 'validate1', 'validate']),
            ('holiday_status_id', 'in', self.ids)
            ('leave_year_id','=',)
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

    