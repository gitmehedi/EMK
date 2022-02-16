from odoo import models, fields,api,_
from psycopg2 import IntegrityError
from odoo.exceptions import UserError, ValidationError


class HrEmployeeLoanType(models.Model):
    _name = 'hr.employee.loan.type'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Employee Loan Type'

    name = fields.Char(size=100, string='Name', required='True', track_visibility='onchange')
    code = fields.Char(size=100, string='Code', required='True', track_visibility='onchange')
    is_interest_payable = fields.Boolean(string='Is Interest Payable', required='True', track_visibility='onchange')
    rate = fields.Float(size=100, string='Rate', track_visibility='onchange')
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange')
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange', )


    """ All relations fields """
    company_id = fields.Many2one('res.company', string='Company', ondelete='cascade',default=lambda self: self.env.user.company_id)
    loan_proof_ids = fields.Many2many(comodel_name='hr.employee.loan.proof',
                                       relation='hr_employee_loan_types_proofs_rel',
                                       column1='types_id',
                                       column2='proofs_id',
                                       string='Loan Proofs')
    loan_policy_ids = fields.Many2many('hr.employee.loan.policy', string='Loan Policies')
    employee_tag_ids = fields.Many2many('hr.employee.category', string='Employee Catagories')


    """ All selection fields """
    interest_mode_id = fields.Selection([
        ('flat', 'Flat'),
        ], string = 'Interest Mode')
    interest_account_id = fields.Selection([
        ('flat', '101200 Account Receivable'),
        ], string = 'Interest Account')
    repayment_method_id = fields.Selection([
        ('payrolldeduction', 'Deduction From Payroll'),
        ], string = 'Repayment Method')
    disburse_method_id = fields.Selection([
        ('payrolldeduction', 'Deirect Cash/Cheque'),
        ], string = 'Disburse Method')


    """All function which process data and operation"""
    @api.constrains('name')
    def _check_unique_constraint(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            # name = self.search(filters)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('draft', 'approve', 'reject'))]

    @api.one
    def act_draft(self):
        if self.state == 'reject':
            self.write({
                'state': 'draft',
                'pending': True,
                'active': False,
            })

    @api.one
    def act_approve(self):
        if self.state == 'draft':
            self.write({
                'state': 'approve',
                'pending': False,
                'active': True,
            })

    @api.one
    def act_reject(self):
        if self.state == 'draft':
            self.write({
                'state': 'reject',
                'pending': False,
                'active': False,
            })

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'reject'):
                raise ValidationError(_(Message.UNLINK_WARNING))
            try:
                return super(HrEmployeeLoanType, rec).unlink()
            except IntegrityError:
                raise ValidationError(_(Message.UNLINK_INT_WARNING))