from odoo import fields, models, api


class InheritedResCompany(models.Model):
    _inherit = 'res.company'

    branch_ids = fields.Many2many('res.branch', string="Functional Units")
