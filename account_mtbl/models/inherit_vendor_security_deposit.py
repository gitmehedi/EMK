from odoo import fields, models


class VendorSecurityDeposit(models.Model):
    _inherit = 'vendor.security.deposit'

    reconcile_ref = fields.Char(string="Reconciliation Ref#", size=20)
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sequence', readonly=True,
                                            track_visibility='onchange', states={'draft': [('readonly', False)]})
