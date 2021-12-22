# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def mailsend(self, vals):
        template = False
        try:
            template = self.env.ref(vals['template'], raise_if_not_found=False)
        except ValueError:
            pass

        assert template._name == 'mail.template'

        template.write({
            'email_to': vals['email_to'] if 'email_to' in vals else '',
            'attachment_ids': vals['attachment_ids'] if 'attachment_ids' in vals else [],
        })

        context = {
            'base_url': self.env['ir.config_parameter'].get_param('web.base.url'),
            'lang': self.env.user.lang,
        }

        for key, val in vals['context'].iteritems():
            context[key] = val

        template.with_context(context).send_mail(self.env.user.id, force_send=True, raise_exception=True)
        _logger.info("Email sending status of user.")

    @api.model
    def mail_send(self, res_id, vals):
        template = False
        try:
            template = self.env.ref(vals['template'], raise_if_not_found=False)
        except ValueError:
            raise ValidationError(_('Mail template not available, please configure mail template.'))

        assert template._name == 'mail.template'

        if 'email_to' in vals:
            template.write({'email_to': vals['email_to'] if 'email_to' in vals else ''})

        if 'attachment_ids' in vals:
            template.write({'attachment_ids': vals['attachment_ids'] if 'attachment_ids' in vals else []})

        context = {
            'base_url': self.env['ir.config_parameter'].get_param('web.base.url'),
            'lang': self.env.user.lang,
        }
        if 'context' in vals:
            for key, val in vals['context'].iteritems():
                context[key] = val

        template.with_context(context).send_mail(res_id, force_send=True, raise_exception=True)
        _logger.info("Email sending status of user.")

    @api.model
    def groupmail(self, val):
        groups = self.env['res.groups'].search(
            [('name', 'in', val['group']), ('category_id.name', '=', val['category'])])
        emails = [str(rec.email) for rec in groups.users if len(rec.create_uid) > 0]
        return ", ".join(emails)
