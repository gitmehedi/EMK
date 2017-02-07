from openerp import models, fields

class HrEmployeeLoanPolicy(models.Model):
    _name = 'hr.employee.loan.policy'    

    name = fields.Char(size=100, string='Name', required='True')
    code_ids = fields.Char(size=100, string='Code', required='True')
    
    """ All relations fields """
    employee_ids = fields.Many2many('hr.employee', string='Loan Proofs')
    employee_tag_ids = fields.Many2many('hr.employee.category', string='Employee catagories')
    
    policy_type_ids = fields.Selection([
        ('flat', 'Max Loan Amount'),
        ('incremental', 'Gap Between Two Loans'),
        ('period', 'Qualifying Period'),
        ], string = 'Policy Type',required='True')
    value_ids = fields.Float(size=100, string='Value', required='True')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    basis_ids = fields.Selection([
        ('flat', 'Fix Amount')], string = 'Basis',required='True')
             