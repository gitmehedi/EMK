from openerp import models, fields, api, exceptions
from datetime

class CalendarHolidayType(models.Model):
    _name='calendar.holiday.type'


    name = fields.Char(size=100, string="Title", required="True")
    status = fields.Boolean(string='Status', default=True)
    year = fields.Char(string='Year')

    # one2many fields

    public_details_ids = fields.One2many('calendar.holiday.type.details', 'public_type_id')
    weekly_details_ids = fields.One2many('calendar.holiday.type.details', 'weekly_type_id')

    @api.multi
    def geneare_yearly_calendar(self):
        vals = {}

        for val in self.public_details_ids:
            vals['name']=val.name
            vals['type']="public"
            vals['date']=val.date
            vals['color']="RED"
            vals['status']=True

            self.env['calendar.holiday'].create(vals)

        for val in self.weekly_details_ids:

            vals['name']= "Weekly Holiday"
            vals['type']="weekly"
            vals['date']=val.date
            vals['color']="Yellow"
            vals['status']=True
            for i in range(365):
                today = datetime.date(datetime.datetime.year.now()
                day_of_year = (today - datetime.datetime(today.year, 1, 1)).days + i
            self.env['calendar.holiday'].create(vals)

        return True