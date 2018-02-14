from odoo import fields, models, api


class InheritUsers(models.Model):
    _inherit = "res.users"

    location_ids = fields.Many2many('stock.location',
                                    'stock_location_users_rel',
                                    'user_id', 'location_id', 'Allow Locations')
    default_location_id = fields.Many2one('stock.location',
                                          'Location')

    # approver_ids = fields.One2many('hr.approver.users', 'user_id', string='Related employees')
    approver_ids = fields.Many2many('hr.employee',string='Related Approvers')


# class HrApproverUsers(models.Model):
#     _name = "hr.approver.users"
#
#     user_id = fields.Many2one('res.users', 'Approver User')
#     employee_id = fields.Many2one('hr.employee', 'Approver User')

