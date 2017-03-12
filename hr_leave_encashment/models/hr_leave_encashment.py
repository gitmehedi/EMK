from openerp import models, fields
from openerp import api

class HrLeaveLeave(models.Model):    
    _name = 'hr.leave.encashment'
    _description = 'HR Leave Encashment'    

    name = fields.Char(size=100, string='Title', required='True')
    encashment_year = fields.Char(size=10, string='Leave Year', required='True')    
    #leave_type = fields.Selection([('earned_leave', 'Earned Leave')], string = 'Leave Type', required='True')
    leave_type = fields.Many2one('hr.holidays.status', string="Leave Type", required='True', ondelete='cascade')
    
    
    """ Relational Fields """
    
    line_ids = fields.One2many('hr.leave.encashment.line','parent_id', string="Line Ids")
    
    
    
  