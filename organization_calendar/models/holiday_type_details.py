from openerp import models, fields, api, exceptions

class CalendarHolidayTypeDetails(models.Model):
    _name='calendar.holiday.type.details'


    name = fields.Char(size=100, string="Title")
    date = fields.Datetime(string="Date")
    weekly_type = fields.Selection([('saturday', 'Saturday'), ('sunday', 'Sunday'),('monday', 'Monday'),('tuesday', 'Tuesday'),('wednesday', 'Wednesday')
                             ,('thursday', 'Thurday'),('friday', 'Friday')])
    status = fields.Boolean(string='Status', default=True)

    # many2one fields

    public_type_id = fields.Many2one('calendar.holiday.type')
    weekly_type_id = fields.Many2one('calendar.holiday.type')
