from odoo import api, fields, models, _


class ResCustomerType(models.Model):
    _inherit = ['mail.thread']

    _name = 'res.customer.type'
    _description = 'Customer Type'

    name = fields.Char(required=True, track_visibility="onchange")

    is_retail = fields.Boolean('Is Retail Customer?', track_visibility="onchange")
    is_corporate = fields.Boolean('Is Corporate Customer?', track_visibility="onchange")
