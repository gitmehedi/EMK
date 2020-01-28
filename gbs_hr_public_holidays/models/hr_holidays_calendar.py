from odoo import models, fields, api, exceptions

class CalendarHoliday(models.Model):
    _name='calendar.holiday'


    name = fields.Char(size=100, string="Title", required="True")
    date = fields.Date(string="Date")
    color = fields.Char(string="Color")
    status = fields.Boolean(string='Status', default=True)
    
    """many2one fields """ 
    
    year_id = fields.Many2one('date.range', string="Leave Year",domain ="[('type_id.holiday_year', '=', True)]")
    
    """ Selection fields """
     
    type = fields.Selection([
        ('weekly', 'Weekly Holiday'),
        ('public', 'Public Holiday')
        ])
