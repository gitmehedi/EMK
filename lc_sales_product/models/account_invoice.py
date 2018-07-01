from odoo import api, fields, models, _

class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    def name_get(self):
        result = []
        for record in self:
            name = record.number
            result.append((record.id, name))
        return result