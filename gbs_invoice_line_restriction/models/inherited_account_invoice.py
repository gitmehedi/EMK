from odoo import fields, models, api


class InheritedAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _default_manual_invoice(self):
        if self._context.get('create_edit_button'):
            return True
        else:
            return False

    manual_invoice = fields.Boolean(default=lambda self: self._default_manual_invoice(), store=True)

