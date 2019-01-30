from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError



class AgreementWizard(models.TransientModel):
    _name = 'agreement.wizard'
    _order = 'name desc'
    _description = 'Vendor Agreement'

    name = fields.Char('Name',readonly=True)
    end_date = fields.Date(string='End Date', required=True,
                           default=lambda self: self.env.context.get('end_date'))
    pro_advance_amount = fields.Float(string="Proposed Advance Amount", required=True,
                                      default=lambda self: self.env.context.get('pro_advance_amount'))

    @api.multi
    def generate(self):
        agr_obj = self.env['agreement'].browse([self._context['active_id']])
        agr_obj.write({
            'end_date': self.end_date,
            'pro_advance_amount': self.pro_advance_amount,
            'rel_id': self.id,
        })

    @api.constrains('end_date')
    def check_end_date(self):
        date = fields.Date.today()
        if self.end_date < date:
            raise ValidationError("Agreement 'End Date' never be less then 'Current Date'.")

    @api.constrains('pro_advance_amount')
    def check_pro_advance_amount(self):
        if self.pro_advance_amount:
            if self.pro_advance_amount < 0:
                raise ValidationError("Please Check Your Proposed Advance Amount!! \n Amount Never Take Negative Value!")

