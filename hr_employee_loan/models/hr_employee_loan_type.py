from openerp import models, fields

class HrEmployeeLoanType(models.Model):
    _name = 'hr.employee.loan.types'

    name = fields.Char(size=100, string='Name', required='True')
    code_ids = fields.Char(size=100, string='Name', required='True')
    is_interest_payable = fields.Boolean(string='Is Interest Payable', required='True')


    """ All relations fields """
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    loan_proofs_ids = fields.Many2many('hr.employee.loan.proof', string = 'Loan Proofs') 
    loan_policy_ids = fields.Many2many('hr.employee.loan.policy', string = 'Loan Policies')
    employee_tag_ids = fields.Many2many('hr.employee.category', string = 'Employee catagories')
    """ All selection fields """
    
    interest_mode = fields.Selection([
        ('flat', 'Flat'),
        ], string = 'Interest Mode',required='True')
    rate = fields.Float(size=100, string='Rate', required='True')
    interest_account = fields.Selection([
        ('flat', '101200 Account Receivable'),
        ], string = 'Interest Account',required='True')
    repayment_method = fields.Selection([
        ('payrolldeduction', 'Deduction From Payroll'),
        ], string = 'Repayment Method',required='True')
    disburse_method = fields.Selection([
        ('payrolldeduction', 'Deirect Cash/Cheque'),
        ], string = 'Disburse Method',required='True')
