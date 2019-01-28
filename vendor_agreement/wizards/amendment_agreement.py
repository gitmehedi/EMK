from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError



class AgreementWizard(models.TransientModel):
    _name = 'agreement.wizard'
    _order = 'name desc'
    _description = 'Vendor Agreement'

    name = fields.Char('Name',readonly=True)
    end_date = fields.Date(string='End Date', required=True,
                           default=lambda self: self.env.context.get('end_date'))

    @api.multi
    def generate(self):
        agr_obj = self.env['agreement'].browse([self._context['active_id']])
        agr_obj.write({
            'end_date': self.end_date,
            'rel_id': self.id,
        })

    @api.constrains('end_date')
    def check_end_date(self):
        date = fields.Date.today()
        if self.end_date < date:
            raise ValidationError("Agreement 'End Date' never be less then 'Current Date'.")


