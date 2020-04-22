from odoo import models, fields, api

class AgreementWarning(models.TransientModel):

    _name = "agreement.warning.wizard"

    text = fields.Char(size=150)
    warning_type = fields.Selection([
        ('reject_amendment', "Reject Amendment"),
        ('inactive_agreement', "Inactive Agreement")], string="Warning Type")

    def action_inactive(self):
        active_id = self.env.context.get('active_id', False)
        agreement = self.env['agreement'].browse(active_id)
        agreement.write({
            'active': False
        })
