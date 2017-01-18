from openerp import models, fields

class HrEmployeeLoanPolicy(models.Model):
    _name = 'hr.employee.loan.policy'    

    name = fields.Char(size=100, string='Name', required='True')
    code = fields.Char(size=100, string='Code', required='True')
    policy_type = fields.Char(size=100, string='Policy Type', required='True')
    value = fields.Float(size=100, string='value', required='True')
             