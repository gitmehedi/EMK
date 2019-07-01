from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError



class AmendmentAgreementWizard(models.TransientModel):
    _name = 'amendment.agreement.wizard'


    name = fields.Char('Name',readonly=True)
    end_date = fields.Date(string='End Date', required=True,
                           default=lambda self: self.env.context.get('end_date'))
    advance_amount_add = fields.Float(string="Advance Amount Addition")
    adjustment_value = fields.Float(string="Adjustment Value", required=True,
                                    default=lambda self: self.env.context.get('adjustment_value'))
    service_value = fields.Float(string="Service Value", required=True,
                                 default=lambda self: self.env.context.get('service_value'))
    account_id = fields.Many2one('account.account',string="Agreement Account",required=True,default=lambda  self: self.env.context.get('account_id'))


    @api.multi
    def generate(self):
        self.env['agreement.history'].create({
            'end_date': self.end_date,
            'advance_amount_add': self.advance_amount_add,
            'adjustment_value': self.adjustment_value,
            'service_value': self.service_value,
            'account_id': self.account_id.id,
            'agreement_id': self._context['active_id'],
        })
        self.env['agreement'].browse(self._context['active_id']).write({'is_amendment': True})

    @api.constrains('end_date')
    def check_end_date(self):
        date = fields.Date.today()
        if self.end_date < date:
            raise ValidationError("Agreement 'End Date' never be less than 'Current Date'.")

    @api.constrains('advance_amount_add','adjustment_value','service_value')
    def check_constrains_amount(self):
        if self.advance_amount_add or self.adjustment_value or self.service_value:
            if self.advance_amount_add < 0:
                raise ValidationError(
                    "Please Check Your Advance Amount Addition!! \n Amount Never Take Negative Value!")
            elif self.adjustment_value < 0:
                raise ValidationError(
                    "Please Check Your Adjustment Value!! \n Amount Never Take Negative Value!")
            elif self.service_value < 0:
                raise ValidationError(
                    "Please Check Your Service Value!! \n Amount Never Take Negative Value!")