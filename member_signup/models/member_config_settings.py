from odoo import fields, models, api, _
from odoo.exceptions import UserError


class MemberConfigSettings(models.TransientModel):
    _name = 'memeber.config.settings'
    _inherit = 'res.config.settings'

    membership_expire = fields.Integer(string="Membership Expire Days", required=True)


    @api.model
    def create(self,vals):
        config_id = super(MemberConfigSettings, self).create( vals)
        return config_id
