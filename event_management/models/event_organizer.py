import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class EventManagementOrganizer(models.Model):
    _inherit = 'res.partner'

    is_organizer = fields.Boolean(default=False, track_visibility='onchange', )
    event_count = fields.Integer("Events", compute='_compute_event_count',
                                 help="Number of events the partner has participated.")
    firstname = fields.Char("First Name", index=True, track_visibility='onchange')
    middlename = fields.Char("Middle Name", index=True, track_visibility='onchange')
    lastname = fields.Char("Last Name", index=True, track_visibility='onchange')
    status = fields.Boolean(default=True, string='Status', track_visibility='onchange')

    def _compute_event_count(self):
        for partner in self:
            partner.event_count = self.env['event.event'].search_count(
                [('organizer_id', '=', partner.id)])

    @api.multi
    def action_event_view(self):
        action = self.env.ref('event.action_event_view').read()[0]
        action['context'] = {}
        action['domain'] = [('organizer_id', '=', self.id)]
        return action

    @api.model
    def event_mailsend(self, vals):
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
            'logo': self.env.user.company_id.logo,
            'lang': self.env.user.lang,
        }

        for key, val in vals['context'].iteritems():
            context[key] = val
        try:
            template.with_context(context).send_mail(self.env.user.partner_id.id, force_send=True, raise_exception=True)
            _logger.info("Email sending status of user.")
        except:
            _logger.info("Email doesn't send properly.")

    @api.multi
    def unlink(self):
        for org in self:
            if org.event_count > 0:
                raise ValidationError(_('You cannot delete a record which has existing event!'))
            if org.user_ids:
                raise ValidationError(_('You cannot delete system user whom has login access!'))
        return super(EventManagementOrganizer, self).unlink()
