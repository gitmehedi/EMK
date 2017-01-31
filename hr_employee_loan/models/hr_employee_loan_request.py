from openerp import models, fields

class HrEmployeeLoanRequest(models.Model):
    _name = 'hr.employee.loan.request'    

    name = fields.Char(size=100, string='Name', required='True')
    code_ids = fields.Char(size=100, string='Code', required='True')
    
    """ All relations fields """
    employee_loan_proofs_ids = fields.Many2many('hr.employee.loan.proof', string = 'Proofs') 
    employee_loan_policies_ids = fields.Many2many('hr.employee.loan.policy', string = 'Policies')
    
    """ All input fields """
    loan_type_ids = fields.Selection([
        ('home_loan', 'Home Loan'),
        ], string = 'Loan Type',required='True')
    applied_date_ids = fields.Char(size=100, string='Applied Date', required='True')
    approved_date_ids = fields.Char(size=100, string='Approved Date', required='True')
    disbursement_date_ids = fields.Char(size=100, string='Disbursement Date', required='True')
    department_ids = fields.Selection([
        ('management', 'Management')], string = 'Department',required='True')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    user_id = fields.Selection([
        ('admin', 'Administrator'),('employee', 'Employee')], string = 'User',required='True')