from odoo import api, fields, models, _
from odoo.addons.opa_utility.helper.utility import Utility
from odoo.exceptions import UserError, ValidationError


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
