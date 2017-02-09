from openerp import models, fields
from openerp import api

class HrEmployeeLoanRequest(models.Model):
    _name = 'hr.employee.loan.request'
    _order = 'name desc'

    name = fields.Char(size=100, string='Loan Name', default="New")
    emp_code = fields.Char(string='Code')
    duration_id = fields.Char(size=100, string='Duration(Months)')
    principal_amount_id = fields.Float(string='Principal Amount')
    notes = fields.Text(string='Notes', size=500, help='Please enter notes.')
    Req_rate = fields.Float(size=100, string='Rate')
    is_interest_payble_id = fields.Boolean(string='Is Interest Payable', required='True')
    
    """ All relations fields """
    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee,
                                  required=True, ondelete='cascade', index=True)
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id")
    employee_loan_proofs_ids = fields.Many2many('hr.employee.loan.proof', string='Proofs')
    employee_loan_policies_ids = fields.Many2many('hr.employee.loan.policy', string='Policies')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    user_id = fields.Many2one('res.users', string='User')
    loan_type_id = fields.Many2one('hr.employee.loan.types', string='Loan Type', required=True)

    """ All Selection fields """
    
    applied_date_id = fields.Datetime('Applied Date', readonly=True, index=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    
    approved_date_id = fields.Datetime('Approved Date', readonly=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    
  
    disbursement_date_id = fields.Datetime('Disbursement Date', readonly=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
         
    interst_mode_id = fields.Selection([
        ('flat', 'Flat'),
        ], string = 'Interest Mode')
    

    state = fields.Selection([
        ('draft', "Draft"),
        ('applied', "Applied"),
        ('approved', "Approved"),
    ], default='draft')


    """ Major functionality """

    '''@api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('emp_code')
        
        return super(HrEmployeeLoanRequest, self).create(vals)'''

#     @api.multi
#     def write(self, vals):
#         vals['name'] = self.env['ir.sequence'].get('emp_code')
#         
#         return super(HrEmployeeLoanRequest, self).write(vals)

    
    """All function which process data and operation"""
    
    @api.onchange('loan_type_id')
    def onchange_loan_type_id(self):
        if self.loan_type_id and self.loan_type_id.loan_proofs_ids:
            self.employee_loan_proofs_ids = self.loan_type_id.loan_proofs_ids
            
        if self.loan_type_id and self.loan_type_id.loan_policy_ids:
            self.employee_loan_policies_ids = self.loan_type_id.loan_policy_ids  
        
    @api.multi
    def action_draft(self):
        self.state = 'draft'
        
    @api.multi
    def action_confirm(self):
        for loan in self:
            loan.state = 'applied'
            loan.name = self.env['ir.sequence'].get('emp_code')
            
    @api.multi
    def action_done(self):
        self.state = 'approved'

