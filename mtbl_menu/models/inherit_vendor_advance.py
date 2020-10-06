from odoo import api, fields, models


class VendorAdvance(models.Model):
    _inherit = 'vendor.advance'

    @api.model
    def _needaction_domain_get(self):
        return ['|', '|', '|', ('state', 'in', ('confirm', 'draft')), ('amount_due', '>', 0),
                ('is_amendment', '=', True), ('is_rejection', '=', True)]
