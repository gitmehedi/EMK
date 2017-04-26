from openerp import models, fields

class HrEmployeeLoanType(models.Model):
    _name = 'hr.employee.loan.type'

    name = fields.Char(size=100, string='Name', required='True')
    code = fields.Char(size=100, string='Name', required='True')
    is_interest_payable = fields.Boolean(string='Is Interest Payable', required='True')

    """ All relations fields """

    company_id = fields.Many2one('res.company', string='Company', ondelete='cascade',default=lambda self: self.env.user.company_id)
    loan_proof_ids = fields.Many2many(comodel_name='hr.employee.loan.proof',
                                       relation='hr_employee_loan_types_proofs_rel',
                                       column1='types_id',
                                       column2='proofs_id',
                                       string='Loan Proofs')

    loan_policy_ids = fields.Many2many('hr.employee.loan.policy', string='Loan Policies')
    employee_tag_ids = fields.Many2many('hr.employee.category', string='Employee catagories')

    """ All selection fields """
    
    interest_mode_id = fields.Selection([
        ('flat', 'Flat'),
        ], string = 'Interest Mode')
    rate = fields.Float(size=100, string='Rate',)
    interest_account_id = fields.Selection([
        ('flat', '101200 Account Receivable'),
        ], string = 'Interest Account',required='True')
    repayment_method_id = fields.Selection([
        ('payrolldeduction', 'Deduction From Payroll'),
        ], string = 'Repayment Method',required='True')
    disburse_method_id = fields.Selection([
        ('payrolldeduction', 'Deirect Cash/Cheque'),
        ], string = 'Disburse Method',required='True')
