from openerp import models, fields

class HrEarnedLeave(models.Model):    
    _inherit = 'hr.holidays.status'    

    earned_leave_flag = fields.Boolean(string='Earned leave flag',default=False)
    
    earned_leave_type = fields.Selection([
        ('yearly', 'Yearly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly')
        ], string = 'Earned Leave Period')