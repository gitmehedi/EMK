from odoo import fields, models, api


class MealSuccessWizard(models.TransientModel):
    _name = 'attendance.success.wizard'

    message = fields.Text('Message')

    def action_yes(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.attendance.import',
            'res_id': self._context['attendance_id'],
            'target': 'main',
            'type': 'ir.actions.act_window'
        }

