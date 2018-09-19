# -*- coding: utf-8 -*-
# © 2015 Salton Massally <smassally@idtlabs.sl>
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    expire_notification_days = fields.Integer(
        string='Notification Days before Expire',
        default=10,
        help="Number of Days before notification send for membership expiration."
    )
    expire_grace_period = fields.Integer(
        default=15,
        string='Membership Grace Period',
        help="Membership grace period before cancel membership."
    )
