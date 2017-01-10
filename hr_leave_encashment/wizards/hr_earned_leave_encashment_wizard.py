from openerp import models, fields
from openerp import api



class HrEarnedLeaveEncashmentWizard(models.TransientModel):
    _name = 'hr.earned.leave.encashment.wizard'
    
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees')
    
    @api.multi
    def process_employee_line(self):
        vals = {}
        chd_obj = self.env['hr.save.encashment.line']
        data = chd_obj.search([('id','=',self.employee_ids.ids)])
        
        if data:
            data.unlink()
        
        for val in self.employee_ids:
            vals['employee_id'] = '1234'
            vals['pending_leave'] = '4'
            vals['leave_days_to_be_encashed'] = '4'
            vals['want_to_encash'] = 'TRUE'

            chd_obj.create(vals)
        
        return True
