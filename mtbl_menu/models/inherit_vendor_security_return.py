from odoo import api, fields, models


class VendorSecurityReturn(models.Model):
    _inherit = 'vendor.security.return'

    @api.model
    def _needaction_domain_get(self):
        return ['|', ('state', 'in', ('confirm', 'draft')), ('amount_due', '>', 0)]
