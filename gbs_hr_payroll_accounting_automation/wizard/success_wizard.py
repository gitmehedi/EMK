from odoo import fields, models, api


class SuccessWizard(models.TransientModel):
    _name = 'success.wizard'

    message = fields.Text('Message')

    def action_yes(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payslip.run',
            'res_id': self._context['payslip_run_id'],
            'target': 'main',
            'type': 'ir.actions.act_window'
        }

