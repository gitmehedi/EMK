from odoo import fields, models, api


class SuccessWizard(models.TransientModel):
    _name = 'return.success.wizard'

    message = fields.Text('Message')

    def action_yes(self):
        return {'type': 'ir.actions.act_window_close'}
