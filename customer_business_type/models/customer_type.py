
from odoo import api, fields, models, _


class ResCustomerType(models.Model):
    _name = 'res.customer.type'
    _description = 'Customer Type'

    name = fields.Char(required=True)
    is_retail = fields.Boolean('Is Retail Customer?')
    is_corporate = fields.Boolean('Is Corporate Customer?')



