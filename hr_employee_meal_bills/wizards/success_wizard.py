from odoo import fields, models, api


class MealSuccessWizard(models.TransientModel):
    _name = 'meal.success.wizard'

    message = fields.Text('Message')

    def action_yes(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.meal.bill',
            'res_id': self._context['meal_bill_id'],
            'target': 'main',
            'type': 'ir.actions.act_window'
        }

