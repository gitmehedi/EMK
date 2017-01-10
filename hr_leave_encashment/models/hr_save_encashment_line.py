from openerp import models, fields
from openerp import api

class HrSaveEncashmentLine(models.Model):    
    _name = 'hr.save.encashment.line'
    _description = 'HR save encashment line'    

    employee_id = fields.Many2one('hr.employee', string="Employee ID")
    pending_leave = fields.Many2one('hr.holidays', string="Pending leave count")
    leave_days_to_be_encashed = fields.Integer(size=100, string='Leave days to be encashed')
    want_to_encash = fields.Boolean(string='Do you want to encash the leave days? ', default=True)
    
