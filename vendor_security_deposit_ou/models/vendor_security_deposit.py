from odoo import api, fields, models


class VendorSecurityDeposit(models.Model):
    _inherit = 'vendor.security.deposit'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid),
                                        readonly=True, states={'draft': [('readonly', False)]})

