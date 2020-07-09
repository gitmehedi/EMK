from odoo import api, fields, models, _


class VendorSecurityDeposit(models.Model):
    _inherit = 'vendor.security.deposit'

    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sequence', readonly=True,
                                            track_visibility='onchange', states={'draft': [('readonly', False)]})
