from datetime import datetime, timedelta

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    mail_notification = fields.Boolean(string='Send Mail', default=False)
    current_membership = fields.Char(string='Current Membership', compute="_compute_current_membership")

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
    def send_invoice_mail_notify(self):
        expire_days = self.env.user.company_id.expire_notification_days
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=expire_days)).strftime('%Y-%m-%d')

        record = self.env['res.partner'].search(
            [('membership_stop', '>=', start_date), ('membership_stop', '<=', end_date)],
            order='membership_days_remaining desc')

        for rec in record:
            if not rec.mail_notification:
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

    @api.multi
    def inactive_user(self):
        self.env.cr.execute("""
                            SELECT 'm.*',
                                   CURRENT_DATE-m.membership_stop AS difference
                            FROM res_partner m
                            INNER JOIN res_users u
	                            ON(u.partner_id=m.id)
                            WHERE CURRENT_DATE-m.membership_stop >%s AND u.active=True
                            ORDER BY difference ASC
                            """, (self.env.user.company_id.expire_grace_period,))

        for rec in self.env.cr.dictfetchall():
            if rec.mail_notification:
                vals = {
                    'template': 'member_signup.member_application_rejection_email_template',
                    'email_to': rec['email'],
                    'context': {'name': rec['email']},
                }
                self.mailsend(vals)
                user = self.env['res.users'].search([('id', '=', rec['id'])])
                if user:
                    user.active = False
