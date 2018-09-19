from odoo import fields, models, api, _
from odoo.exceptions import UserError


class MemberConfigSettings(models.TransientModel):
    _name = 'memeber.config.settings'
    _inherit = 'res.config.settings'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id)

    expire_notification_days = fields.Integer(
        string='Notification Days Before Expire',
        related='company_id.expire_notification_days',
        help="Number of Days before notification send for membership expiration.",
        required=True
    )
    expire_grace_period = fields.Integer(
        string='Membership Grace Period',
        related='company_id.expire_grace_period',
        help="Membership grace period before cancel membership.",
        required=True
    )
