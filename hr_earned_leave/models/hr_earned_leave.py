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
        'Dou you want to carry forward your leave ',
        help="If enabled, public holidays are skipped in leave days "
        "calculation.", default=True) 
    earned_leave_encashment = fields.Boolean(
        'Dou you want to encash your earned leave ',
        help="If enabled, public holidays are skipped in leave days "
        "calculation.", default=True) 
    # help="If enabled, public holidays are skipped in leave days "
    