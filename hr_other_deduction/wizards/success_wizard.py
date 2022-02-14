from odoo import fields, models, api


class OtherDeductionSuccessWizard(models.TransientModel):
    _name = 'other.deduction.success.wizard'

    message = fields.Text('Message')

    def action_yes(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.other.deduction',
            'res_id': self._context['deduction_id'],
            'target': 'main',
            'type': 'ir.actions.act_window'
        }

