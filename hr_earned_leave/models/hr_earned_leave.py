from openerp import models, fields

class HrEarnedLeave(models.Model):    
    _inherit = 'hr.holidays.status'    

    earned_leave_type = fields.Selection([
        ('yearly', 'Yearly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly')
        ])
    
       