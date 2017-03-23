# -*- coding: utf-8 -*-
# ©  2016 Md Mehedi Hasan <md.mehedi.info@gmail.com>.

from datetime import datetime, time
from openerp import models, api
import calendar


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def work_scheduled_on_day(self, date_dt, public_holiday=True,
                              schedule=True):
        ''''
        returns true or false depending on if employee was scheduled to work
        on a particular day. It does this by both checking if it is a public
        holiday and the resource calendar of the contract
        @param date_dt: date for which to check
        @param public_holiday: optional, whether to consider public holidays,
                               default=True
        @param schedule: optional, whether to consider the contract's resource
                         calendar. default=True
        '''
        week_day_obj = self.env['hr.holidays.public']
        weekly_obj = week_day_obj.search([('year','=',date_dt.year)])
        weeks_name = tuple([(w.weekly_type).title() for w in weekly_obj.weekly_details_ids])
        
        self.ensure_one()
        
        if public_holiday and week_day_obj.is_public_holiday(date_dt, employee_id=self.id):
            return False
        elif schedule and self.contract_id and self.contract_id.working_hours:
            hours = self.contract_id.working_hours.get_working_hours_of_date(datetime.combine(date_dt, time.min))[0]
        
            if not hours:
                return False
        elif schedule and (not self.contract_id or (self.contract_id and not self.contract_id.working_hours)):
            return calendar.day_name[date_dt.weekday()] not in weeks_name

        return True
