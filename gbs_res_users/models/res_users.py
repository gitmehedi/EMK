from odoo import fields, models, api

class InheritUsers(models.Model):
    _inherit = "res.users"

    location_ids = fields.Many2many('stock.location',
                                    'stock_location_users_rel',
                                    'user_id', 'location_id', 'Allow Locations')
    default_location_id = fields.Many2one('stock.location',
                                          'Location')