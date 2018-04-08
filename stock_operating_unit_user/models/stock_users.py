from odoo import fields, models, api,_
from odoo.exceptions import ValidationError

class InheritUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _get_default_location(self):
        return self.env['stock.location'].search([('operating_unit_id','=',self.default_operating_unit_id.id)], limit=1)

    location_ids = fields.Many2many('stock.location',
                                    'stock_location_users_rel',
                                    'user_id', 'location_id', 'Allow Locations',domain="[('usage', '!=', 'view')]")
    default_location_id = fields.Many2one('stock.location',
                                          default=_get_default_location,
                                          string='Default Location')

    @api.multi
    @api.constrains('default_location_id', 'location_ids')
    def _check_location(self):
        if any(user.location_ids and user.default_location_id not in user.location_ids for user in self):
            raise ValidationError(_('The chosen location is not in the allowed locations for this user'))