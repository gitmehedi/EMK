from openerp import models, fields

class HrEmployeeLoanType(models.Model):
    _name = 'hr.employee.loan.types'

    name = fields.Char(size=100, string='Name', required='True')
    is_interest_payable = fields.Boolean(string='Is Interest Payable', default=True)
    interest_mode = fields.Selection([
        ('flat', 'Flat'),
        ('incremental', 'Incremenatal'),
        ], string = 'Interest Mode')
    rate = fields.Float(size=100, string='Rate', required='True')
    repayment_method = fields.Selection([
        ('payrolldeduction', 'Deduction From Payroll'),
        ('manual', 'Manual'),
        ], string = 'Repayment Method')
    disburse_method = repayment_method = fields.Selection([
        ('payrolldeduction', 'Deduction From Payroll'),
        ('manual', 'Manual'),
        ], string = 'Disburse Method')
    company = fields.Char(size=100, string='Company', required='True')
    #company = fields.One2many('res.company', string = 'Company', readonly = True)
    loan_proofs = fields.Many2many('hr.employee.loan.proof', string = 'Loan Proofs', readonly = True) 
