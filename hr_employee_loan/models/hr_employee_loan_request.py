from openerp import models, fields

class HrEmployeeLoanRequest(models.Model):
    _name = 'hr.employee.loan.request'    

    employee_id = fields.Char(size=100, string='Employee Name', required='True')
    name = fields.Char(size=100, string='Number', required='True')
    duration_ids = fields.Char(size=100, string='Duration(Months)', required='True')
    principal_amount_ids = fields.Float(string='Principal Amount')
    notes=fields.Text(string='Notes', size=500, help='Please enter notes.')
    is_interest_payble_ids = fields.Boolean(string='Is Interest Payable', required='True')
    """ All relations fields """
    employee_loan_proofs_ids = fields.Many2many('hr.employee.loan.proof', string = 'Proofs') 
    employee_loan_policies_ids = fields.Many2many('hr.employee.loan.policy', string = 'Policies')
    
    
    """ All Selection fields """
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
    
    state = fields.Selection([('draft', "Draft"), ('applied', "Applied"), ('approved', "Approved")],
                            default="draft", readonly=True, track_visibility='onchange')
    interst_mode_ids = fields.Selection([
        ('flat', 'Flat'),
        ], string = 'Interest Mode',required='True')
    rate_ids = fields.Float(size=100, string='Rate', required='True')
    
    
