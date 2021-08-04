from odoo import models, fields, api, _


class ResPartner(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'mail.thread', 'ir.needaction_mixin']

    @api.multi
    def notify_due_invoice(self):
        record = self.browse(self._context.get('active_ids'))
        for rec in record:
            vals = {
                'template': 'member_payment.member_notification_for_due_invoice',
                'email_to': rec.partner_id.email,
                'context': {'name': rec.partner_id.name},
            }
            self.env['res.partner'].mailsend(vals)


    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'open')]
