from openerp import models, fields
import datetime
from dateutil.relativedelta import relativedelta
from openerp import api


class HrEmployeeLoanRequest(models.Model):
    _name = 'hr.employee.loan'
    _order = 'name desc'

    name = fields.Char(size=100, string='Loan Name', default="New")
    emp_code_id = fields.Char(string='Code')
    duration = fields.Integer(size=100, string='Duration(Months)',required=True,
                states={'draft': [('invisible', False)], 'applied': [('readonly', True)], 'approved':[('readonly', True)],'disbursed':[('readonly', True)]})
    principal_amount = fields.Float(string='Principal Amount',required=True,
                        states={'draft': [('invisible', False)], 'applied': [('readonly', True)], 'approved':[('readonly', True)],'disbursed':[('readonly', True)]})
    notes = fields.Text(string='Notes', size=500, help='Please enter notes.',
                        states={'draft': [('invisible', False)], 'applied': [('readonly', True)], 'approved':[('readonly', True)],'disbursed':[('readonly', True)]})
    req_rate = fields.Float(size=100, string='Rate',required=True,
                            states={'draft': [('invisible', False)], 'applied': [('readonly', True)], 'approved': [('readonly', True)],'disbursed':[('readonly', True)]})
    is_interest_payble = fields.Boolean(string='Is Interest Payable', required='True',
                        states={'draft': [('invisible', False)], 'applied': [('readonly', True)], 'approved':[('readonly', True)],'disbursed':[('readonly', True)]})
    applied_date = fields.Datetime('Applied Date', readonly=True, copy=False,
        states={'draft': [('invisible', True)], 'applied': [('readonly', True)], 'approved':[('readonly', True)],'disbursed':[('readonly', True)]})
    
    approved_date = fields.Datetime('Approved Date', readonly=True, copy=False,
        states={'draft': [('invisible', True)], 'applied': [('invisible', True)], 'approved':[('readonly', True)],'disbursed':[('readonly', True)]})

    repayment_date = fields.Date('Repayment Date',required=True,states={'draft': [('invisible', False)], 'applied': [('readonly', True)], 'approved':[('readonly', True)],'disbursed':[('readonly', True)]})

    disbursement_date = fields.Datetime('Disbursement Date', readonly=True, copy=False,
        states={'draft': [('invisible', True)], 'applied': [('invisible', True)], 'approved':[('readonly', True)],'disbursed':[('readonly', True)]})

    remaining_loan_amount = fields.Float(string="Remaining Loan", digits=(15, 2), compute="_compute_loan_amount", store=True)
    
    """ All relations fields """
    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    line_ids = fields.One2many('hr.employee.loan.line', 'parent_id', string="Employee Loan Installment Details",
                               states={'draft': [('invisible', False)], 'applied': [('readonly', True)],
                                       'approved': [('readonly', True)], 'disbursed': [('readonly', True)]})

    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee,
                                  required=True, ondelete='cascade', index=True,
                                  states={'draft': [('invisible', False)], 'applied': [('readonly', True)], 'approved':[('readonly', True)],'disbursed':[('readonly', True)]})
    department_id = fields.Many2one('hr.department', string="Department",ondelete='cascade', related="employee_id.department_id")
    employee_loan_proof_ids = fields.Many2many('hr.employee.loan.proof', string='Proofs',
                                states={'draft': [('invisible', False)], 'applied': [('readonly', True)], 'approved':[('readonly', True)],'disbursed':[('readonly', True)]})
    employee_loan_policy_ids = fields.Many2many('hr.employee.loan.policy', string='Policies',
                                    states={'draft': [('invisible', False)], 'applied': [('readonly', True)], 'approved':[('readonly', True)],'disbursed':[('readonly', True)]})
    company_id = fields.Many2one('res.company', string='Company',ondelete='cascade', default=lambda self: self.env.user.company_id)
    user_id = fields.Many2one('res.users', string='User')
    loan_type_id = fields.Many2one('hr.employee.loan.type', string='Loan Type', required=True,ondelete='cascade',
                                   states={'draft': [('invisible', False)], 'applied': [('readonly', True)], 'approved':[('readonly', True)],'disbursed':[('readonly', True)]})

    """ All Selection fields """
    interst_mode_id = fields.Selection([
        ('flat', 'Flat'),
        ], string = 'Interest Mode',
        states={'draft': [('invisible', False)], 'applied': [('readonly', True)], 'approved': [('readonly', True)],'disbursed':[('readonly', True)]})

    state = fields.Selection([
        ('draft', "Draft"),
        ('applied', "Applied"),
        ('approved', "Approved"),
        ('disbursed', "Disbursed"),
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
    def action_disbursed(self):
        self.state = 'disbursed'

    @api.multi
    def action_draft(self):
        for loan in self:
            loan.state = 'applied'
            loan.applied_date = datetime.datetime.now()
            loan.name = self.env['ir.sequence'].get('emp_code_id')

    @api.multi
    def action_done(self):
        for loan in self:
            loan.state = 'approved'
            loan.approved_date = datetime.datetime.now()
            loan.disbursement_date = datetime.datetime.now()

    @api.multi
    def generate_schedules(self):
        for loan in self:
            if loan.duration > 0 and loan.repayment_date and len(loan.line_ids)==0:
                repayment_date = datetime.datetime.strptime(loan.repayment_date, '%Y-%m-%d')
                installment_amount = loan.principal_amount / int(loan.duration)
                loan.line_ids.unlink()
                for i in range(1, loan.duration+1):
                    vals = {}
                    vals['employee_id'] = loan.employee_id.id
                    vals['schedule_date'] = repayment_date
                    vals['installment'] = installment_amount
                    vals['num_installment'] = i
                    vals['parent_id'] = loan.id
                    repayment_date = repayment_date + relativedelta(months=1)
                    loan.line_ids.create(vals)

    @api.constrains('name')
    def _check_unique_constraint(self):
        if self.name:
            filters = [['name', '=ilike', self.name]]
            name = self.search(filters)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.depends('line_ids')
    def _compute_loan_amount_with_payslip(self):
        for loan in self:
            self.remaining_loan_amount = sum([l.installment for l in loan.line_ids if l.state=='pending'])

    @api.constrains('duration','principal_amount')
    def _check_qty(self):
        if self.duration < 0 or self.principal_amount < 0:
            raise Warning('principal_amount or duration cannot be negative !')

