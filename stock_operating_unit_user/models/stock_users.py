from odoo import fields, models, api,_
from odoo.exceptions import ValidationError

class InheritUsers(models.Model):
    _inherit = "res.users"

    # @api.model
    # def _get_default_location(self):
    #     return self.env['stock.location'].search([('operating_unit_id','=',self.default_operating_unit_id.id)], limit=1)

    # compute = '_compute_default_location',
    default_location_id = fields.Many2one('stock.location',
                                          string='Default Location',
                                          domain="[('usage', '!=', 'view')]")
    location_ids = fields.Many2many('stock.location',
                                    'stock_location_users_rel',
                                    'user_id', 'location_id', 'Allow Locations', domain="[('usage', '!=', 'view')]")

    @api.multi
    @api.constrains('default_location_id', 'location_ids')
    def _check_location(self):
        if any(user.location_ids and user.default_location_id not in user.location_ids for user in self):
            raise ValidationError(_('The chosen location is not in the allowed locations for this user'))

    # @api.multi
    # @api.onchange('default_operating_unit_id')
    # def _onchange_default_operating_unit(self):
    #     for user in self:
    #         if user.default_location_id:
    #             user.location_ids = []
    #             user.default_location_id = self.env['stock.location'].search([('operating_unit_id','=',self.default_operating_unit_id.id)])

