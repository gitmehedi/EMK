from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def act_due_invoice(self):
        record = self.browse(self._context.get('active_ids'))
        for rec in record:
            rec.env['res.partner'].sendinvoice(rec)
