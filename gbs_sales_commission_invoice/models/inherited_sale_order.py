from odoo import fields, api, models


class InheritedSaleOrderLine(models.Model):
    _inherit = 'account.invoice.line'

    commission_rate = fields.Float(string="Com. (%)")
    is_commission_paid = fields.Boolean(string="Is Commission Paid?", default=False)
