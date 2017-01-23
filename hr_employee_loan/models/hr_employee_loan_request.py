from openerp import models, fields

class HrEmployeeLoanRequest(models.Model):
    _name = 'hr.employee.loan.request'    

    name = fields.Char(size=100, string='Name', required='True')
    code = fields.Char(size=100, string='Code', required='True')
    loan_type = fields.Char(size=100, string='Loan Type', required='True')
    policy_type = fields.Char(size=100, string='Policy Type', required='True')
    employee_name = fields.Char(size=100, string='Employee Name', required='True')
   
    
             