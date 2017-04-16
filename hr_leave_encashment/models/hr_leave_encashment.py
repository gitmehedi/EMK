from openerp import models, fields
from openerp import api

class HrEarnedLeave(models.Model):    
    _inherit = 'hr.holidays.status'
    
    earned_leave_encashment = fields.Boolean(
        'Encash this leave ',
        help="If enabled, employee will be able to encash their leave", default=True) 

class HrLeaveLeave(models.Model):    
    _name = 'hr.leave.encashment'
    _description = 'HR Leave Encashment'    

    name = fields.Char(size=100, string='Title', required='True')
    encashment_year = fields.Char(size=10, string='Leave Year', required='True')    
    leave_type = fields.Many2one('hr.holidays.status', string="Leave Type", required='True', 
                                 ondelete='cascade',domain=[('earned_leave_encashment','=',True)])
    
    
    """ Relational Fields """
    
    line_ids = fields.One2many('hr.leave.encashment.line','parent_id', string="Line Ids")
    
    
    
  