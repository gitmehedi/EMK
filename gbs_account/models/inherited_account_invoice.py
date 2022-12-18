from odoo import fields, models, api


class InheritedAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    from_return = fields.Boolean(default=False)
