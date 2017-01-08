from openerp import models, fields
from openerp import api



class HrEarnedLeaveEncashmentWizard(models.TransientModel):
    _name = 'hr.earned.leave.encashment.wizard'
    
    
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees')
    
#     name = fields.Integer(size=100, string='Employee ID', required='True')
#     dept_name = fields.Char(size=100, string='Dept Name', required='True')
#     pending_leave = fields.Integer(size=100, string='Pending Leave', required='True')
#     allowed_leave = fields.Integer(size=100, string='Allowed Leave', required='True')
#     is_leave_encashed = fields.Boolean(size=100, string='Do you want to Carry Forward the leave? ', required='True')
    
     
    @api.multi
    def compute_sheet(self):
        vals = {}
        chd_obj = self.env['hr.employee']
        #data = chd_obj.search([('id','=',self.year_id.id)])
         
        vals['id'] =  employee_id       
        chd_obj.create(vals)
         
        return True
