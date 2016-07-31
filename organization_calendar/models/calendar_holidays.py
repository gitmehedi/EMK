from openerp import models, fields, api, exceptions

class CalendarHoliday(models.Model):
    _name='calendar.holiday'


    name = fields.Char(size=100, string="Title", required="True")
    type = fields.Selection([('weekly', 'Weekly Holiday'),('public', 'Public Holiday')])
    date = fields.Datetime(string="Date")
    color = fields.Char(string="Color")
    status = fields.Boolean(string='Status', default=True)

