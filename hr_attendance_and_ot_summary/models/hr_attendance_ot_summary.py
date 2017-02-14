from openerp import models, fields
from openerp import api

class HrAttendanceOTSummary(models.Model):    
    _name = 'hr.attendance.ot.summary'
    _description = 'Attendance and over time summary'    

    name = fields.Char(size=100, string='Title', required='True')       
    period = fields.Char(size=100, string='Period', required='True')        
    
    """ Relational Fields """
    
    line_ids = fields.One2many('hr.attendance.ot.summary.line','parent_id', string="Line Ids")
    
    
    
  