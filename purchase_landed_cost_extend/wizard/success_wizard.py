from odoo import fields, models, api


class LCSuccessWizard(models.TransientModel):
    _name = 'landed.cost.success.wizard'

    message = fields.Text('Message')

    def action_yes(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.cost.distribution',
            'res_id': self._context['distribution_id'],
            'target': 'main',
            'type': 'ir.actions.act_window'
        }

