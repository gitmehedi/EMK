from odoo import fields, models, api


class InheritUsers(models.Model):
    _inherit = "res.users"

    approver_ids = fields.Many2many('hr.employee', string='Related Approvers')