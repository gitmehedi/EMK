from odoo import fields, models


class AccountTaxSlabLine(models.Model):
    _inherit = 'account.tax.slab.line'

    vendor_advance_id = fields.Many2one('vendor.advance')
