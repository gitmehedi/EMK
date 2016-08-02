from openerp import models, fields, api, exceptions
import datetime,time

class CalendarHolidayType(models.Model):
    _name='calendar.holiday.type'


    name = fields.Char(size=100, string="Title", required="True")
    status = fields.Boolean(string='Status', default=True)

    # Many2one fields
    year_id = fields.Many2one('account.fiscalyear',string="Calender Year")

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
            vals['color']="Yellow"
            vals['status']=True

            if not self.year_id.date_start:
                raise exceptions.ValidationError("Please provide start date of fiscal year")
            if not self.year_id.date_stop:
                raise exceptions.ValidationError("Please provide end date of fiscal year")

            start_date = self.year_id.date_start.split('-')
            end_date = self.year_id.date_stop.split('-')

            days= datetime.datetime(int(end_date[0]),int(end_date[1]),int(end_date[2]))-datetime.datetime(int(start_date[0]),int(start_date[1]),int(start_date[2]))

            noOfDays= days.days+1
            curTime = time.mktime(datetime.datetime(int(start_date[0]),int(start_date[1]),int(start_date[2])).timetuple())

            for i in range(noOfDays):
                searchTime = (i * 86400 + curTime)
                dayName = datetime.datetime.fromtimestamp(int(searchTime))
                if dayName.strftime('%A') == val.weekly_type.title():
                    vals['date'] = dayName
                    self.env['calendar.holiday'].create(vals)

        return True




