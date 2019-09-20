from odoo import api, fields, models, _


class Employee(models.Model):

    _inherit = "hr.employee"

    tax_zone = fields.Char('Tax Zone')
    tax_circle = fields.Char('Tax Circle')
    tax_location = fields.Char('Tax Location')
