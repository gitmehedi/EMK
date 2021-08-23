from odoo import models, fields, api


class MessageBoxWizard(models.TransientModel):
    _name = "message.box.wizard"

    text = fields.Text()
