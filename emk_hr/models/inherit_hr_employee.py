from odoo import api, fields, models, _
from odoo.addons.opa_utility.helper.utility import Utility
from odoo.exceptions import UserError, ValidationError
from psycopg2 import IntegrityError


class Employee(models.Model):

    _inherit = "hr.employee"

    tax_zone = fields.Char('Tax Zone')
    tax_circle = fields.Char('Tax Circle')
    tax_location = fields.Char('Tax Location')
    bank_account_number = fields.Char('Bank Account Number')

    @api.one
    @api.constrains('work_phone')
    def valid_mobile(self):
        if self.work_phone:
            if not Utility.valid_mobile(self.work_phone):
                raise ValidationError('Personal mobile no should be input a valid')

    @api.one
    @api.constrains('mobile_phone')
    def valid_mobile(self):
        if self.work_phone:
            if not Utility.valid_mobile(self.work_phone):
                raise ValidationError('Work mobile no should be input a valid')

    @api.one
    @api.constrains('bank_account_number')
    def valid_bank_account_number(self):
        if self.bank_account_number:
            if len(self.bank_account_number) > 17:
                raise ValidationError('Bank account no should be input a valid')


class HrEmployeeContractType(models.Model):
    _inherit = ['hr.contract.type']

    active = fields.Boolean(string='Active', default=False, track_visibility='onchange')
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange', )

    @api.constrains('name')
    def _check_name(self):
        name = self.search(
            [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
             ('active', '=', False)])
        if len(name) > 1:
            raise ValidationError(_('[DUPLICATE] Name already exist, choose another.'))

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
                return super(HrEmployeeContractType, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))

