from openerp import models, fields, api, exceptions
import datetime,time

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

            vals['color']="Yellow"
            vals['status']=True

            days = 365
            curTime = time.mktime(datetime.datetime(2016, 1, 1).timetuple())

            for i in range(days):
                searchTime = (i * 86400 + curTime)
                dayName = datetime.datetime.fromtimestamp(int(searchTime))
                print val.weekly_type,"------------------------"
                if dayName.strftime('%A') == val.weekly_type.title():
                    vals['date'] = dayName
                    print "----------------",vals
                    self.env['calendar.holiday'].create(vals)

        return True

    def getTimeStramp(year, day):
        days = 365
        curTime = time.mktime(datetime.datetime(year, 1, 1).timetuple())

        for i in range(days):
            searchTime = (i * 86400 + curTime)
            dayName = datetime.datetime.fromtimestamp(int(searchTime))
            if dayName.strftime('%A') in day:
                print dayName