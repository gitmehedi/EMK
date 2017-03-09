from openerp import models, fields

class HrEarnedLeave(models.Model):    
    _inherit = 'hr.holidays.status'    

    earned_leave_flag = fields.Boolean(string='Earned leave flag',default=False)
    
    earned_leave_type = fields.Selection([
        ('yearly', 'Yearly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly')
        ], string = 'Earned Leave Period')
    
    leave_carry_forward = fields.Boolean(
        'Carry Forward this leave',
        help="If enabled, employee will be able to carry fwd leaves "
        "calculation.", default=True) 
    earned_leave_encashment = fields.Boolean(
        'Encash this leave ',
        help="If enabled, employee will be able to encash their leave", default=True) 
    