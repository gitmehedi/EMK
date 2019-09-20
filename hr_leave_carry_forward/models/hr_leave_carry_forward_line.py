from odoo import models, fields, api

class HrLeaveCarryForwardtLine(models.Model):    
    _name = 'hr.leave.carry.forward.line'
    _description = 'HR save carry forward line'    
    
    pending_leave = fields.Integer(string="Pending leave count")
    leave_days_to_be_caryy_forwarded = fields.Integer(size=100, string='Leave days to be carry forwarded', 
                                                      readonly=True)
    want_to_carry_forward = fields.Boolean(string='Do you want to carry forward the leave days? ', 
                                           default=True)
#
    """ Relational Fields """
    
    parent_id = fields.Many2one('hr.leave.carry.forward')
    employee_id = fields.Many2one('hr.employee', string="Employee ID",ondelete='cascade')
    
