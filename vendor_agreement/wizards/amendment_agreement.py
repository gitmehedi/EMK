from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError



class AmendmentAgreementWizard(models.TransientModel):
    _name = 'amendment.agreement.wizard'


    name = fields.Char('Name',readonly=True)
    end_date = fields.Date(string='End Date', required=True,
                           default=lambda self: self.env.context.get('end_date'))
    pro_advance_amount = fields.Float(string="Proposed Advance Amount", required=True,
                                      default=lambda self: self.env.context.get('pro_advance_amount'))

    adjustment_value = fields.Float(string="Adjustment Value", required=True,
                                    default=lambda self: self.env.context.get('adjustment_value'))
    service_value = fields.Float(string="Service Value", required=True,
                                 default=lambda self: self.env.context.get('service_value'))
    account_id = fields.Many2one('account.account',string="Agreement Account",required=True,default=lambda  self: self.env.context.get('account_id'))


    @api.multi
    def generate(self):
        agr_obj = self.env['agreement'].browse([self._context['active_id']])
        agr_obj.write({
            'end_date': self.end_date,
            'pro_advance_amount': self.pro_advance_amount,
            'adjustment_value': self.adjustment_value,
            'service_value': self.service_value,
            'account_id': self.account_id.id,
            'rel_id': self.id,
        })

    @api.constrains('end_date')
    def check_end_date(self):
        date = fields.Date.today()
        if self.end_date < date:
            raise ValidationError("Agreement 'End Date' never be less then 'Current Date'.")

    @api.constrains('pro_advance_amount')
    def check_pro_advance_amount(self):
        if self.pro_advance_amount or self.adjustment_value or self.service_value:
            if self.pro_advance_amount < 0:
                raise ValidationError(
                    "Please Check Your Proposed Advance Amount!! \n Amount Never Take Negative Value!")
            elif self.adjustment_value < 0:
                raise ValidationError(
                    "Please Check Your Adjustment Value!! \n Amount Never Take Negative Value!")
            elif self.service_value < 0:
                raise ValidationError(
                    "Please Check Your Service Value!! \n Amount Never Take Negative Value!")