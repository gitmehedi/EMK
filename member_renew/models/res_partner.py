from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    mail_notification = fields.Boolean(string='Mail Notification', default=False)

    @api.multi
    def notify_expiration(self):
        record = self.browse(self._context.get('active_ids'))
        for rec in record:
            vals = {
                'template': 'member_renew.member_renew_notification_email_template',
                'email': rec['email'],
                'email_cc': 'nopaws_ice_iu@yahoo.com,mahtab.faisal@genweb2.com',
                'attachment_ids': 'member_renew.member_renew_notification_email_template',
                'context': {},
            }
            self.mailsend(vals)
            rec.mail_notification = True
