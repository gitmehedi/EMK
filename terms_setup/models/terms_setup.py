from odoo import fields, models, api,_

class TermsSetup(models.Model):
    _name = "terms.setup"

    name = fields.Char(string = 'Name',required=True)
    terms_condition = fields.Text(string='Terms & Conditions', required=True)
