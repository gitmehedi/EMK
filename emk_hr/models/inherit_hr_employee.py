import datetime
from psycopg2 import IntegrityError
import dateutil.parser
from odoo import api, fields, models, _
from odoo.addons.opa_utility.helper.utility import Utility,Message
from odoo.exceptions import UserError, ValidationError



class Employee(models.Model):
    _inherit = "hr.employee"

    tax_zone = fields.Char('Tax Zone')
    tax_circle = fields.Char('Tax Circle')
    tax_location = fields.Char('Tax Location')
    bank_account_number = fields.Char('Bank Account Number')
    mobile_phone = fields.Char('Personal Mobile')
    gender = fields.Many2one('res.gender', string='Gender', track_visibility='onchange')
    pre_email = fields.Char(string="Present Email", required=True, track_visibility='onchange')

    per_street = fields.Char(string='Street',required=True, track_visibility='onchange')
    per_street2 = fields.Char(string='ETC', track_visibility='onchange')
    per_zip = fields.Char(track_visibility='onchange')
    per_city = fields.Char(string='City', track_visibility='onchange')
    per_state_id = fields.Many2one('res.country.state', track_visibility='onchange')
    per_country_id = fields.Many2one('res.country',required=True, track_visibility='onchange',
                                 default=lambda self: self.env.user.company_id.country_id.id)

    pre_street = fields.Char(string='Street',required=True, track_visibility='onchange')
    pre_street2 = fields.Char(string='ETC', track_visibility='onchange')
    pre_zip = fields.Char(track_visibility='onchange')
    pre_city = fields.Char(string='City', track_visibility='onchange')
    pre_state_id = fields.Many2one('res.country.state',track_visibility='onchange')
    pre_country_id = fields.Many2one('res.country', required=True,track_visibility='onchange',
                                     default=lambda self: self.env.user.company_id.country_id.id)

    @api.one
    @api.constrains('pre_email')
    def validate_mail(self):
        if self.pre_email:
            if not Utility.valid_email(self.pre_email):
                raise ValidationError('Present email should be input a valid')

    @api.one
    @api.constrains('work_phone')
    def valid_work_phone(self):
        if self.work_phone:
            if not Utility.valid_mobile(self.work_phone):
                raise ValidationError('Personal mobile no should be input a valid')

    @api.one
    @api.constrains('mobile_phone')
    def valid_mobile(self):
        if self.mobile_phone:
            if not Utility.valid_mobile(self.mobile_phone):
                raise ValidationError('Work mobile no should be input a valid')

    @api.one
    @api.constrains('bank_account_number')
    def valid_bank_account_number(self):
        if self.bank_account_number:
            if len(self.bank_account_number) > 17:
                raise ValidationError('Bank account no should be input a valid')

    @api.one
    @api.constrains('birthday')
    def valid_birthdate(self):
        if self.birthday:
            birthdate = dateutil.parser.parse(self.birthday).date()
            if birthdate > datetime.datetime.now().date():
                raise ValidationError(_('[Warning] Employee date of birth should be past date'))

    @api.one
    @api.constrains('fam_father_date_of_birth')
    def valid_father_birthdate(self):
        if self.fam_father_date_of_birth:
            birthdate = dateutil.parser.parse(self.fam_father_date_of_birth).date()
            if birthdate > datetime.datetime.now().date():
                raise ValidationError(_('[Warning] Father date of birth should be past date'))

    @api.one
    @api.constrains('fam_mother_date_of_birth')
    def valid_mother_birthdate(self):
        if self.fam_mother_date_of_birth:
            birthdate = dateutil.parser.parse(self.fam_mother_date_of_birth).date()
            if birthdate > datetime.datetime.now().date():
                raise ValidationError(_('[Warning] Mother date of birth should be past date'))

    @api.onchange('user_id')
    def _onchange_user(self):
        if self.user_id:
            self.work_email = self.work_email
            self.name = self.name
            self.image = self.image
            user = self.search([('user_id', '=', self.user_id.id)])
            if len(user) > 0:
                raise ValidationError(_('[DUPLICATE] Related user already exist, choose another.'))

    # @api.one
    # @api.onchange('user_id')
    # def _check_user_id(self):
    #     if self.user_id.id:
    #         user = self.search([('user_id', '=', self.user_id.id)])
    #         if len(user) > 0:
    #             raise ValidationError(_('[DUPLICATE] Related user already exist, choose another.'))


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
            raise ValidationError(_(Message.UNIQUE_WARNING))

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
                return super(HrEmployeeContractType, rec).unlink()
            except IntegrityError:
                raise ValidationError(_(Message.UNLINK_INT_WARNING))


class HrEmployeeChildren(models.Model):
    _inherit = 'hr.employee.children'

    @api.one
    @api.constrains('date_of_birth')
    def valid_birthdate(self):
        if self.date_of_birth:
            birthdate = dateutil.parser.parse(self.date_of_birth).date()
            if birthdate > datetime.datetime.now().date():
                raise ValidationError(_('[Warning] Children date of birth should be past date'))

class HrEmployeeContract(models.Model):
    _inherit = ['hr.contract']

    @api.one
    def act_draft(self):
        if self.state == 'open':
            self.write({
                'state': 'close',
            })

    @api.one
    def act_approve(self):
        if self.state == 'draft':
            self.write({
                'state': 'open',

            })

    @api.one
    def act_renew(self):
        if self.state == 'open':
            self.write({
                'state': 'pending',

            })

    @api.one
    def act_reject(self):
        if self.state == 'open':
            self.write({
                'state': 'close',
            })

