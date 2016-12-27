from openerp import models, fields

class LeaveCarryForward(models.Model):
    _name = 'hr.leave.carry.forward'
    _description = 'HR Leave Carry Forward'
    
    name = fields.Char(size=100, string='Title', required='True')
    carry_foward_year = fields.Char(size=10, string='Leave Year', required='True')    
    leave_type = fields.Many2one('hr.holidays.status', string="Leave Type", required='True')
    