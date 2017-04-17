from openerp import models, fields
import datetime
from dateutil.relativedelta import relativedelta
from openerp import api


class HrEmployeeLoanRequest(models.Model):
    _name = 'hr.employee.loan'
    _order = 'name desc'

    name = fields.Char(size=100, string='Loan Name', default="New")
    emp_code = fields.Char(string='Code')
    duration = fields.Integer(size=100, string='Duration(Months)',required=True,
                states={'draft': [('invisible', False)], 'applied': [('readonly', True)], 'approved':[('readonly', True)]})
    principal_amount = fields.Float(string='Principal Amount',required=True,
                        states={'draft': [('invisible', False)], 'applied': [('readonly', True)], 'approved':[('readonly', True)]})
    notes = fields.Text(string='Notes', size=500, help='Please enter notes.',
                        states={'draft': [('invisible', False)], 'applied': [('readonly', True)], 'approved':[('readonly', True)]})
    req_rate = fields.Float(size=100, string='Rate',required=True)
    is_interest_payble = fields.Boolean(string='Is Interest Payable', required='True',
                        states={'draft': [('invisible', False)], 'applied': [('readonly', True)], 'approved':[('readonly', True)]})
    applied_date = fields.Datetime('Applied Date', readonly=True, copy=False,
        states={'draft': [('invisible', True)], 'applied': [('readonly', True)], 'approved':[('invisible', True)]})
    
    approved_date = fields.Datetime('Approved Date', readonly=True, copy=False,
        states={'draft': [('invisible', True)], 'applied': [('invisible', True)], 'approved':[('readonly', True)]})

    repayment_date = fields.Date('Repayment Date',required=True)

    line_ids = fields.One2many('hr.employee.loan.line', 'parent_id', string="Line Ids")

    disbursement_date = fields.Datetime('Disbursement Date', readonly=True, copy=False,
        states={'draft': [('invisible', True)], 'applied': [('invisible', True)], 'approved':[('readonly', True)]})
    
    """ All relations fields """
    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)


    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee,
                                  required=True, ondelete='cascade', index=True,
                                  states={'draft': [('invisible', False)], 'applied': [('readonly', True)], 'approved':[('readonly', True)]})
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id")
    employee_loan_proof_ids = fields.Many2many('hr.employee.loan.proof', string='Proofs',
                                states={'draft': [('invisible', False)], 'applied': [('readonly', True)], 'approved':[('readonly', True)]})
    employee_loan_policy_ids = fields.Many2many('hr.employee.loan.policy', string='Policies',
                                    states={'draft': [('invisible', False)], 'applied': [('readonly', True)], 'approved':[('readonly', True)]})
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    user_id = fields.Many2one('res.users', string='User')
    loan_type_id = fields.Many2one('hr.employee.loan.type', string='Loan Type', required=True,
                                   states={'draft': [('invisible', False)], 'applied': [('readonly', True)], 'approved':[('readonly', True)]})

    """ All Selection fields """
         
    interst_mode_id = fields.Selection([
        ('flat', 'Flat'),
        ], string = 'Interest Mode',)
    

    state = fields.Selection([
        ('draft', "Draft"),
        ('applied', "Applied"),
        ('approved', "Approved"),
    ], default='draft')
    
    """All function which process data and operation"""
    @api.onchange('loan_type_id')
    def onchange_loan_type_id(self):
        if self.loan_type_id and self.loan_type_id.loan_proof_ids:
            self.employee_loan_proof_ids = self.loan_type_id.loan_proof_ids
            
        if self.loan_type_id and self.loan_type_id.loan_policy_ids:
            self.employee_loan_policy_ids = self.loan_type_id.loan_policy_ids  
        
    @api.multi
    def action_confirm(self):
        self.state = 'draft'

    @api.multi
    def action_draft(self):
        for loan in self:
            loan.state = 'applied'
            loan.applied_date = datetime.datetime.now()
            loan.name = self.env['ir.sequence'].get('emp_code')

    @api.multi
    def action_done(self):
        for loan in self:
            loan.state = 'approved'
            loan.approved_date = datetime.datetime.now()
            loan.disbursement_date = datetime.datetime.now()

    @api.multi
    def generate_schedules(self):
        line_pool = self.env['hr.employee.loan.line']
        for loan in self:
            if loan.duration > 0 and loan.repayment_date:
                repayment_date = datetime.datetime.strptime(loan.repayment_date, '%Y-%m-%d')
                installment_amount = loan.principal_amount / int(loan.duration)
                for i in range(1, loan.duration+1):
                    vals = {}
                    vals['employee_id'] = loan.employee_id.id
                    vals['schedule_date'] = repayment_date
                    vals['installment'] = installment_amount
                    vals['num_installment'] = i
                    vals['parent_id'] = loan.id
                    repayment_date = repayment_date + relativedelta(months=1)

                    line_pool.create(vals)





