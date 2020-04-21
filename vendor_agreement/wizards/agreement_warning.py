from odoo import models, fields, api

class AgreementWarning(models.TransientModel):

    _name = "agreement.warning.wizard"

    text = fields.Char(size=150)
    warning_type = fields.Selection([
        ('reject_amendment', "Reject Amendment"),
        ('inactive_agreement', "Inactive Agreement")], string="Warning Type")
