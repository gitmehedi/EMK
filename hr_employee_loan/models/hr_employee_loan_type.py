from openerp import models, fields

class HrEmployeeLoanType(models.Model):
    _name = 'hr.employee.loan.types'

    name = fields.Char(size=100, string='Name', required='True')
    code_ids = fields.Char(size=100, string='Name', required='True')
    is_interest_payable = fields.Boolean(string='Is Interest Payable', required='True')
    interest_mode = fields.Selection([
        ('flat', 'Flat'),
        ('incremental', 'Incremenatal'),
        ], string = 'Interest Mode',required='True')
    rate = fields.Float(size=100, string='Rate', required='True')
    interest_account = fields.Selection([
        ('flat', 'Flat'),
        ('incremental', 'Incremenatal'),
        ], string = 'Interest Account',required='True')
    repayment_method = fields.Selection([
        ('payrolldeduction', 'Deirect From Payroll'),
        ('manual', 'Manual'),
        ], string = 'Repayment Method',required='True')
    disburse_method = fields.Selection([
        ('payrolldeduction', 'Deirect Cash/Cheque'),
        ('manual', 'Manual'),
        ], string = 'Disburse Method',required='True')
    company_ids = fields.Char(size=100, string='Company', required='True')
    #company = fields.One2many('res.company', string = 'Company', readonly = True)
    loan_proofs_ids = fields.Many2many('hr.employee.loan.proof', string = 'Loan Proofs') 
    employee_tag_ids = fields.Many2many('hr.employee.', string = 'Employee catagories')
