from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    mail_notification = fields.Boolean(string='Send Mail', default=False)
    current_membership = fields.Char(string='Current Membership',compute="_compute_current_membership")

    @api.multi
    def _compute_current_membership(self):
        for rec in self:
            if len(rec.member_lines) > 0:
                for mem in rec.member_lines:
                    if rec.membership_stop == mem.date_to:
                        rec.current_membership = mem.membership_id.name

    @api.multi
    def notify_expiration(self):
        record = self.browse(self._context.get('active_ids'))
        for rec in record:
            vals = {
                'template': 'member_renew.member_renew_notification_email_template',
                'email_to': rec['email'],
                'context': {},
            }
            self.mailsend(vals)
            rec.mail_notification = True

    @api.multi
    def renew_requst(self):
        record = self.browse(self._context.get('active_ids'))
        for rec in record:
            if rec['auto_renew']:
                self._create_invoice()
                rec.mail_notification = True
            else:
                vals = {
                    'template': 'member_renew.member_renew_notification_email_template',
                    'email_to': rec['email'],
                    'context': {'name': rec['name'], 'expire_date': rec['membership_stop']},
                }
                self.mailsend(vals)
                rec.mail_notification = True

                object = {
                    'membership_id': self.id,
                    'request_date': fields.Date.today(),
                    'state': 'request',
                }
                self.env['renew.request'].create(object)
