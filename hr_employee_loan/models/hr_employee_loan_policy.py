from odoo import models, fields,api,_
from psycopg2 import IntegrityError
from odoo.exceptions import UserError, ValidationError


class HrEmployeeLoanPolicy(models.Model):
    _name = 'hr.employee.loan.policy'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Employee loan policy'

    name = fields.Char(size=100, string='Name', required='True', track_visibility='onchange')
    code = fields.Char(size=100, string='Code', required='True', track_visibility='onchange')
    value = fields.Float(size=100, string='Value', track_visibility='onchange')
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange')
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange', )

    
    """ All relations fields """
    employee_ids = fields.Many2many('hr.employee', string='''Employee's''')
    employee_tag_ids = fields.Many2many('hr.employee.category', string='Employee Catagories')
    company_id = fields.Many2one('res.company', string='Company',ondelete='cascade', default=lambda self: self.env.user.company_id)


    """ All Selection fields """
    policy_type_id = fields.Selection([
        ('flat', 'Max Loan Amount'),
        ('incremental', 'Gap Between Two Loans'),
        ('period', 'Qualifying Period'),
        ], string = 'Policy Type')

    basis_id = fields.Selection([
        ('flat', 'Fix Amount')], string = 'Basis')



    """All function which process data and operation"""
    @api.constrains('name')
    def _check_unique_constraint(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[DUPLICATE] Name already exist, choose another.')

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
                raise ValidationError(_('[Warning] Approves and Rejected record cannot be deleted.'))
            try:
                return super(HrEmployeeLoanPolicy, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))
