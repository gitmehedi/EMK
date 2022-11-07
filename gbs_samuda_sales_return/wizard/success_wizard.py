from odoo import fields, models, api


class SuccessWizard(models.TransientModel):
    _name = 'return.success.wizard'

    message = fields.Text('Message')

    def action_yes(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'res_id': self._context['picking_id'],
            'target': 'main',
            'type': 'ir.actions.act_window'
        }

