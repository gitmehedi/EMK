from odoo import fields, models, api


class OtherAllowanceSuccessWizard(models.TransientModel):
    _name = 'other.allowance.success.wizard'

    message = fields.Text('Message')

    def action_yes(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.other.allowance',
            'res_id': self._context['allowance_id'],
            'target': 'main',
            'type': 'ir.actions.act_window'
        }

