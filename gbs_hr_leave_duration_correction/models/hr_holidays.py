from openerp import fields, models, api
from datetime import date
import math
from datetime import timedelta
from openerp.exceptions import UserError, ValidationError

HOURS_PER_DAY = 8

class HRHolidays(models.Model):
    _inherit = 'hr.holidays'

    date_from = fields.Date('Start Date', readonly=True, index=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    date_to = fields.Date('End Date', readonly=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})

    number_of_days_temp = fields.Float('Allocation', readonly=True, copy=False,
                                       states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    number_of_days = fields.Float('Number of Days', compute='_compute_number_of_days', store=True)


    """
       As we removed Datetime data type so we have added 1d with date difference -- rabbi
    """
    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        from_dt = fields.Datetime.from_string(date_from)
        to_dt = fields.Datetime.from_string(date_to)

        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            resource = employee.resource_id.sudo()
            if resource and resource.calendar_id:
                hours = resource.calendar_id.get_working_hours(from_dt, to_dt, resource_id=resource.id,
                                                               compute_leaves=True)
                uom_hour = resource.calendar_id.uom_id
                uom_day = self.env.ref('product.product_uom_day')
                if uom_hour and uom_day:
                    return uom_hour._compute_quantity(hours, uom_day)

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
            raise ValidationError(('Start Date should be less than the End Date'))

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
            raise ValidationError(('End Date should be greater than the Start Date'))
