from odoo import models, fields, api,_


class BudgetBillWizard(models.TransientModel):
    _name = 'budget.bill.wizard'

    name = fields.Char(string="Massage",readonly=True,
                       default=lambda self: self.env.context.get('default_msg'))