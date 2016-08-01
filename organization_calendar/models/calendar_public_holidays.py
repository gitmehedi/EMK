#all public holiday

from openerp import models, fields, api, exceptions

class CalendarPublicHoliday(models.Model):
    _name='calendar.public.holiday'


    name = fields.Char(size=100, string="Title", required="True")
    type = state = fields.Selection([('weekly', 'Weekly Holiday'),('public', 'Public Holiday')], required="True")
    date = fields.Date(string="Date",default=fields.Date.today(), required=True)
