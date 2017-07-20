from odoo import models, fields
import datetime
from datetime import datetime
from datetime import timedelta
from odoo import api
from odoo.exceptions import UserError, AccessError, ValidationError

HOURS_PER_DAY = 8

class HrShortLeave(models.Model):
    _name = 'hr.short.leave'
    _inherit = 'hr.holidays'
    _description = "Short Leave"

    date_from = fields.Datetime('Start Date', readonly=True, index=True, copy=False,
                                states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    date_to = fields.Datetime('End Date', readonly=True, copy=False,
                              states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})

    # @api.model
    # def create(self, values):
    #     return super(HrShortLeave, self).create(values)
    #
    #
    # @api.multi
    # def write(self, values):
    #     return super(HrShortLeave, self).write(values)

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
            if (date_from[:10] == date_to[:10]): #only date is equal
                # Compute and update the number of days
                if (date_to and date_from) and (date_from <= date_to):
                    self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
                else:
                    self.number_of_days_temp = 0
            else:
               raise ValidationError('Start Date and End Date should be same')
