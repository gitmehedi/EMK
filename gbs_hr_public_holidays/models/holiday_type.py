import datetime
import time
from odoo import fields, models, api,exceptions


class CalendarHolidayType(models.Model):
    _name = 'calendar.holiday.type'


    name = fields.Char(size=100, string="Title", required="True")
    status = fields.Boolean(string='Status', default=True)

    """ many2one fields """ 
    year_id = fields.Many2one('account.fiscalyear', string="Calender Year")

    """ one2many fields """
    public_details_ids = fields.One2many('hr.holidays.public.line', 'public_type_id')
    weekly_details_ids = fields.One2many('hr.holidays.public.line', 'weekly_type_id')

    """ Custom activity """
    
    @api.multi
    def geneare_yearly_calendar(self):
        vals = {}
        chd_obj = self.env["calendar.holiday"]
        data = chd_obj.search([('year_id','=',self.year_id.id)])
        
        if data:
            data.unlink()
        
        for val in self.public_details_ids:
            vals['name'] = val.name
            vals['type'] = "public"
            vals['date'] = val.date
            vals['color'] = "RED"
            vals['status'] = True

            chd_obj.create(vals)

        for val in self.weekly_details_ids:
            vals['name'] = "Weekly Holiday"
            vals['type'] = "weekly"
            vals['color'] = "Yellow"
            vals['status'] = True
            vals['year_id'] = self.year_id.id

            if not self.year_id.date_start:
                raise exceptions.ValidationError("Please provide start date of fiscal year")
            if not self.year_id.date_end:
                raise exceptions.ValidationError("Please provide end date of fiscal year")

            start_date = self.year_id.date_start.split('-')
            end_date = self.year_id.date_end.split('-')

            days = datetime.datetime(int(end_date[0]), int(end_date[1]), int(end_date[2]))-datetime.datetime(int(start_date[0]), int(start_date[1]), int(start_date[2]))

            noOfDays = days.days + 1
            curTime = time.mktime(datetime.datetime(int(start_date[0]), int(start_date[1]), int(start_date[2])).timetuple())

            for i in range(noOfDays):
                searchTime = (i * 86400 + curTime)
                dayName = datetime.datetime.fromtimestamp(int(searchTime))
                if dayName.strftime('%A') == val.weekly_type.title():
                    vals['date'] = dayName
                    chd_obj.create(vals)

        raise exceptions.ValidationError("Calendar Generate Successfully")
        return True
 




