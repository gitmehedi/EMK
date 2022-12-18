from odoo import fields, models, api


class InheritedResCompany(models.Model):
    _inherit = 'res.company'

    customer_types = fields.Many2many('res.customer.type', string="Customer Business Type")
