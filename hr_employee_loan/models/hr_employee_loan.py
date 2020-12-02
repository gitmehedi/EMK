import datetime

from dateutil.relativedelta import relativedelta
from odoo import api
from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError


class HrEmployeeLoanRequest(models.Model):
    _name = 'hr.employee.loan'
    _inherit = ['mail.thread']
    _order = 'name desc'
    _description = 'Employee Loan'

    name = fields.Char(size=100, string='Loan Name', default="/")
    emp_code_id = fields.Char(string='Code')
    installment_amount = fields.Integer(size=100, string='Installment Amount', required=True,
                                        states={'draft': [('invisible', False)], 'applied': [('readonly', True)],
                                                'approved': [('readonly', True)], 'disbursed': [('readonly', True)]})
    principal_amount = fields.Float(string='Principal Amount', required=True,
                                    states={'draft': [('invisible', False)], 'applied': [('readonly', True)],
                                            'approved': [('readonly', True)], 'disbursed': [('readonly', True)]})
    notes = fields.Text(string='Notes', size=500, help='Please enter notes.',
                        states={'draft': [('invisible', False)], 'applied': [('readonly', True)],
                                'approved': [('readonly', True)], 'disbursed': [('readonly', True)]})
    req_rate = fields.Float(size=100, string='Rate', required=True,
                            states={'draft': [('invisible', False)], 'applied': [('readonly', True)],
                                    'approved': [('readonly', True)], 'disbursed': [('readonly', True)]})
    is_interest_payble = fields.Boolean(string='Is Interest Payable', required='True',
                                        states={'draft': [('invisible', False)], 'applied': [('readonly', True)],
                                                'approved': [('readonly', True)], 'disbursed': [('readonly', True)]})
    # remaining_loan_amount = fields.Float(string="Remaining Loan", digits=(15, 2), compute="_compute_loan_amount", store=True)

    """ All datetime fields """
    applied_date = fields.Datetime('Applied Date', readonly=True, copy=False,
                                   states={'draft': [('invisible', True)], 'applied': [('readonly', True)],
                                           'approved': [('readonly', True)], 'disbursed': [('readonly', True)]})

    approved_date = fields.Datetime('Approved Date', readonly=True, copy=False,
                                    states={'draft': [('invisible', True)], 'applied': [('invisible', True)],
                                            'approved': [('readonly', True)], 'disbursed': [('readonly', True)]})

    repayment_date = fields.Date('Repayment Date', required=True, default=datetime.datetime.now(),
                                 states={'draft': [('invisible', False)], 'applied': [('readonly', True)],
                                         'approved': [('readonly', True)], 'disbursed': [('readonly', True)]})

    disbursement_date = fields.Datetime('Disbursement Date', readonly=True, copy=False,
                                        states={'draft': [('invisible', True)], 'applied': [('invisible', True)],
                                                'approved': [('readonly', True)], 'disbursed': [('readonly', True)]})

    remaining_loan_amount = fields.Float(string="Remaining Loan", digits=(15, 2), readonly=True,
                                         compute='_compute_loan_amount_with_payslip',
                                         states={'draft': [('invisible', True)], 'applied': [('invisible', True)],
                                                 'approved': [('invisible', True)],
                                                 'disbursed': [('invisible', False)]})

    """ All relations fields """

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    line_ids = fields.One2many('hr.employee.loan.line', 'parent_id', string="Employee Loan Installment Schedule",
                               states={'draft': [('invisible', False)], 'applied': [('readonly', True)],
                                       'approved': [('readonly', True)], 'disbursed': [('readonly', True)]})

    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee,
                                  required=True, ondelete='cascade', index=True,
                                  states={'draft': [('invisible', False)], 'applied': [('readonly', True)],
                                          'approved': [('readonly', True)], 'disbursed': [('readonly', True)]})
    department_id = fields.Many2one('hr.department', string="Department", ondelete='cascade',
                                    related="employee_id.department_id")
    employee_loan_proof_ids = fields.Many2many('hr.employee.loan.proof', string='Proofs',
                                               relation='employee_loan_proof_rel',
                                               states={'draft': [('invisible', False)], 'applied': [('readonly', True)],
                                                       'approved': [('readonly', True)],
                                                       'disbursed': [('readonly', True)]})
    employee_loan_policy_ids = fields.Many2many('hr.employee.loan.policy', relation='employee_loan_policy_rel',
                                                string='Policies',
                                                states={'draft': [('invisible', False)],
                                                        'applied': [('readonly', True)],
                                                        'approved': [('readonly', True)],
                                                        'disbursed': [('readonly', True)]})
    company_id = fields.Many2one('res.company', string='Company', ondelete='cascade',
                                 default=lambda self: self.env.user.company_id, readonly='True')
    user_id = fields.Many2one('res.users', string='User')
    loan_type_id = fields.Many2one('hr.employee.loan.type', string='Loan Type', required=True, ondelete='cascade',
                                   states={'draft': [('invisible', False)], 'applied': [('readonly', True)],
                                           'approved': [('readonly', True)], 'disbursed': [('readonly', True)]})

    """ All Selection fields """
    interst_mode_id = fields.Selection([
        ('flat', 'Flat'),
    ], string='Interest Mode',
        states={'draft': [('invisible', False)], 'applied': [('readonly', True)], 'approved': [('readonly', True)],
                'disbursed': [('readonly', True)]})

    state = fields.Selection([
        ('draft', "Draft"),
        ('applied', "Applied"),
        ('approved', "Approved"),
        ('disbursed', "Disbursed"),
        ('closed', "Closed"),
    ], default='draft')

    """All function which process data and operation"""

    @api.model
    def create(self, values):
        loan = super(HrEmployeeLoanRequest, self).create(values)
        if loan:
            loan.employee_loan_policy_ids = loan.loan_type_id.loan_policy_ids
            loan.employee_loan_proof_ids = loan.loan_type_id.loan_proof_ids

        return loan

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
        self.generate_schedules()
        self.state = 'disbursed'
        self.remaining_loan_amount = self.principal_amount
        self.disbursement_date = datetime.datetime.now()

    @api.multi
    def check_policy(self, loan_id, state):
        warning = False
        warning_msg = "Warning!!!Please check the following issues!!!\n"
        blocker = False
        blocker_msg = "Loan Request can not be applied because of the following reasons:\n"

        for policy in loan_id.employee_loan_policy_ids:
            rec = {
                'loan_amount': loan_id.principal_amount,
                'policy': policy,
                'employee_id': loan_id.employee_id.id
            }
            if policy.check_on_application and state == "apply":

                result = self._check_individual_policy(rec)

                if not result['state']:
                    if policy.application_blocker_type == 'warning':
                        warning = True
                        warning_msg = warning_msg + "\n" + result['msg']
                    elif policy.application_blocker_type == 'blocker':
                        blocker = True
                        blocker_msg = blocker_msg + "\n" + result['msg']

            elif policy.check_on_approval and state == "approve":

                result = self._check_individual_policy(rec)

                if not result['state']:
                    if policy.approval_blocker_type == 'warning':
                        warning = True
                        warning_msg = warning_msg + "\n" + result['msg']
                    elif policy.approval_blocker_type == 'blocker':
                        blocker = True
                        blocker_msg = blocker_msg + "\n" + result['msg']

        res = {
            'warning': warning,
            'blocker': blocker,
            'warning_msg': warning_msg,
            'blocker_msg': blocker_msg
        }
        return res

    @api.multi
    def action_draft(self):
        for loan in self:
            if loan.principal_amount <= 0 or loan.installment_amount <= 0:
                raise ValidationError(_('Principle Amount and Installment Amount must be greater than Zero!!!'))
            check_state = "apply"
            policy_data = self.check_policy(loan, check_state)
            if policy_data['blocker']:
                raise ValidationError(_(policy_data['blocker_msg']))
            elif policy_data['warning']:
                return {
                    'id': 'view_loan_apply_warning',
                    'name': 'Loan Warning',
                    'type': 'ir.actions.act_window',
                    'res_model': 'hr.employee.loan.apply.warning',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'target': 'new'
                }
            else:
                self.action_apply(loan)

    @api.multi
    def action_apply(self, loan):
        loan.state = 'applied'
        loan.applied_date = datetime.datetime.now()
        loan.name = self.env['ir.sequence'].get('emp_code_id')

    @api.multi
    def action_done(self):
        for loan in self:
            check_state = "approve"
            policy_data = self.check_policy(loan, check_state)
            if policy_data['blocker']:
                raise ValidationError(_(policy_data['blocker_msg']))
            elif policy_data['warning']:
                return {
                    'id': 'view_loan_approve_warning',
                    'name': 'Loan Warning',
                    'type': 'ir.actions.act_window',
                    'res_model': 'hr.employee.loan.approve.warning',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'target': 'new'
                }
            else:
                self.action_approve(loan)

    @api.multi
    def action_approve(self, loan):
        loan.state = 'approved'
        loan.approved_date = datetime.datetime.now()

    @api.multi
    def generate_schedules(self):
        for loan in self:
            if loan.installment_amount > 0 and loan.repayment_date and len(loan.line_ids) == 0:
                repayment_date = datetime.datetime.strptime(loan.repayment_date, '%Y-%m-%d')
                # installment = loan.principal_amount / int(loan.installment_amount)
                loan.line_ids.unlink()
                p_amount = loan.principal_amount
                i = 1
                while p_amount > 0:
                    vals = {}
                    vals['employee_id'] = loan.employee_id.id
                    vals['schedule_date'] = repayment_date
                    if p_amount > loan.installment_amount:
                        vals['installment'] = loan.installment_amount
                    else:
                        vals['installment'] = p_amount
                    vals['num_installment'] = i
                    vals['parent_id'] = loan.id
                    repayment_date = repayment_date + relativedelta(months=1)
                    loan.line_ids.create(vals)
                    i += 1
                    p_amount -= loan.installment_amount

    @api.depends('line_ids', 'principal_amount')
    def _compute_loan_amount_with_payslip(self):
        for loan in self:
            loan.remaining_loan_amount = sum([l.installment for l in loan.line_ids if l.state == 'pending'])

            # Show a msg for minus value

    @api.constrains('installment_amount', 'principal_amount', 'req_rate')
    def _check_qty(self):
        if self.installment_amount < 0 or self.principal_amount < 0 or self.req_rate < 0:
            raise Warning('Principal Amount or installment_amount or Rate never take negative value!')

    @api.multi
    def unlink(self):
        for loan in self:
            if loan.state != 'draft':
                raise UserError(_('You can not delete this.'))
            loan.line_ids.unlink()
        return super(HrEmployeeLoanRequest, self).unlink()

    def _check_individual_policy(self, loan_info):
        policy = loan_info['policy']
        loan_amount = loan_info['loan_amount']
        state = True
        msg = ""

        if policy.policy_type_id == 'flat':
            if policy.basis_id == 'flat':
                if policy.value < loan_amount:
                    state = False
                    msg = msg + "Policy On Max Limit:" + "\n" + "--Principal Amount is exceeding the Maximum Loan Limit"

            elif policy.basis_id == 'percentage':
                emp_id = loan_info['employee_id']
                self._cr.execute(
                    "SELECT employee_id,wage FROM hr_contract WHERE employee_id = {0} ORDER BY date_start DESC LIMIT 1".format(
                        emp_id))
                query_data = self._cr.fetchall()
                if query_data[0]:
                    employee_wage = query_data[0][1]
                max_limit = (employee_wage * policy.value) / 100
                if max_limit < loan_info['loan_amount']:
                    state = False
                    msg = msg + "Policy On Percentage of Wage:" + "\n" + \
                          "--Principal Amount is exceeding the Maximum Limit according to the wage of your latest contract"

        res = {
            'state': state,
            'msg': msg
        }
        return res

    @api.one
    def check_pending_installment(self):
        for line in self.line_ids:
            if line.state == 'pending':
                return False
        return True
