from openerp import models, fields, api, exceptions

class CalendarHoliday(models.Model):
    _name='calendar.holiday'


    name = fields.Char(size=100, string="Title", required="True")
    date = fields.Date(string="Date")
    color = fields.Char(string="Color")
    status = fields.Boolean(string='Status', default=True)
    
    """many2one fields """ 
    
    year_id = fields.Many2one('account.fiscalyear', string="Calender Year")
    
    """ Selection fields """
     
    type = fields.Selection([
        ('weekly', 'Weekly Holiday'),
        ('public', 'Public Holiday')
        ])
