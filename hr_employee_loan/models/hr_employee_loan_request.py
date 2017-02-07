from openerp import models, fields
from openerp import api

class HrEmployeeLoanRequest(models.Model):
    _name = 'hr.employee.loan.request'
    _order = 'name desc'

    name = fields.Char(size=100, string='Loan Name', default="New")
    # emp_code = fields.Char(size=100)
    duration_ids = fields.Char(size=100, string='Duration(Months)')
    principal_amount_ids = fields.Float(string='Principal Amount')
    notes = fields.Text(string='Notes', size=500, help='Please enter notes.')
    rate_ids = fields.Float(size=100, string='Rate')
    is_interest_payble_ids = fields.Boolean(string='Is Interest Payable', required='True')
    
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
    
    applied_date_ids = fields.Datetime('Applied Date', readonly=True, index=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    
    approved_date_ids = fields.Datetime('Approved Date', readonly=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    
  
    disbursement_date_ids = fields.Datetime('Disbursement Date', readonly=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
         
    interst_mode_ids = fields.Selection([
        ('flat', 'Flat'),
        ], string = 'Interest Mode')
    

    state = fields.Selection([
        ('draft', "Draft"),
        ('applied', "Applied"),
        ('approved', "Approved"),
    ], default='draft')


    """ Major functionality """


    @api.model
    def create(self, vals):
        # employee_loan_policies_ids
        loan_type_obj = self.env['hr.employee.loan.types']
        loan_ids = loan_type_obj.search([('id','=',vals['loan_type_id'])])
        policy_ids = loan_type_obj.search([('id','=',vals['loan_policy_ids'])])

        loan_list = [i for i in loan_ids]
        policy_list = [i for i in policy_ids]

        vals['employee_loan_proofs_ids'][0][2] = list(set(vals['employee_loan_proofs_ids'][0][2])-set(loan_list))
        vals['employee_loan_policies_ids'][0][2] = list(set(vals['employee_loan_policies_ids'][0][2])-set(policy_list))

        loan_ids.loan_proofs_ids = vals['employee_loan_proofs_ids']
        policy_ids.loan_proofs_ids = vals['employee_loan_policies_ids']

        return super(HrEmployeeLoanRequest, self).create(vals)

    @api.multi
    def write(self, vals):
        loan_type_obj = self.env['hr.employee.loan.types']
        loan_ids = loan_type_obj.search([('id', '=', vals['loan_type_id'])])
        policy_ids = loan_type_obj.search([('id', '=', vals['loan_policy_ids'])])

        loan_list = [i for i in loan_ids]
        policy_list = [i for i in policy_ids]

        vals['employee_loan_proofs_ids'][0][2] = list(set(vals['employee_loan_proofs_ids'][0][2]) - set(loan_list))
        vals['employee_loan_policies_ids'][0][2] = list(
            set(vals['employee_loan_policies_ids'][0][2]) - set(policy_list))

        loan_ids.loan_proofs_ids = vals['employee_loan_proofs_ids']
        policy_ids.loan_proofs_ids = vals['employee_loan_policies_ids']

        return super(HrEmployeeLoanRequest, self).write(vals)


    @api.onchange('loan_type_id')
    def _onchange_loan_type_id(self):
        res, ids = {}, []
        # self.loan_type_id = 0
        # self.export_po_id = 0

        if self.loan_type_id:
            res['domain'] = {
                'employee_loan_proofs_ids': [('id', 'in', self.loan_type_id.loan_proofs_ids.ids)],
            }

        return res

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

