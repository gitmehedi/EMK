from openerp import models, fields

class HrEmployeeLoanType(models.Model):
    _name = 'hr.employee.loan.type'    

    name = fields.Char(size=100, string='Name', required='True')
    is_interest_payable = fields.Boolean(string='Is Interest Payable', default=True)
    interest_mode = fields.Char(size=100, string='Interest Mode', required='True')
    rate = fields.Float(size=100, string='Rate', required='True')
    repayment_method = fields.Char(size=100, string='Repayment Method', required='True')
    disburse_method = fields.Char(size=100, string='Disburse Method', required='True')
    company = fields.Char(size=100, string='Company', required='True')
    
             