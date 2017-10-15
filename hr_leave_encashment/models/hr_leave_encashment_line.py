from odoo import models, fields

class HrLeaveEncashmentLine(models.Model):    
    _name = 'hr.leave.encashment.line'
    _description = 'HR save encashment line'    

    
    pending_leave = fields.Integer(string="Pending leave count")
    leave_days_to_be_encashed = fields.Integer(size=100, string='Leave days to be encashed', 
                                               readonly=True)
    want_to_encash = fields.Boolean(string='Do you want to encash the leave days? ', 
                                    default=True)
#     
    """ Relational Fields """
    
    parent_id = fields.Many2one('hr.leave.encashment', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string="Employee ID", ondelete='cascade')
    
