from odoo import fields, models, api


class ArrearSuccessWizard(models.TransientModel):
    _name = 'arrear.success.wizard'

    message = fields.Text('Message')

    def action_yes(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payroll.arrear',
            'res_id': self._context['arrear_id'],
            'target': 'main',
            'type': 'ir.actions.act_window'
        }

