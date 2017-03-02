from openerp import models, fields
from openerp import api

class HrLeaveLeave(models.Model):    
    _name = 'hr.leave.carry.forward'
    _description = 'HR Leave carry forward'    

    name = fields.Char(size=100, string='Title', required='True')
    carry_forward_year = fields.Char(size=10, string='Leave Year', required='True')
    leave_type = fields.Many2one('hr.holidays.status', string="Leave Type", required='True')
    
    
    """ Relational Fields """
    
    line_ids = fields.One2many('hr.leave.carry.forward.line','parent_id', string="Line Ids")
    
    
    
  