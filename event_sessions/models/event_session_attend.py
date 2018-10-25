# -*- coding: utf-8 -*-

import pytz

from odoo import _, api, fields, models
from odoo.addons.mail.models.mail_template import format_tz
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import html_translate

from dateutil.relativedelta import relativedelta


class EventSessionAttend(models.Model):
    _name = 'event.session.attend'
    _description = 'Attendee'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'event_id, create_date desc'

    session_id = fields.Many2one(comodel_name='event.session', string='Session', ondelete='cascade', )
    origin = fields.Char(string='Source Document', readonly=True,
                         help="Reference of the document that created the registration, for example a sale order")
    event_id = fields.Many2one('event.event', string='Event', required=True, readonly=True,
                               states={'draft': [('readonly', False)]})
    date_open = fields.Datetime(string='Registration Date', readonly=True,
                                default=lambda self: fields.datetime.now())  # weird crash is directly now
    date_closed = fields.Datetime(string='Attended Date', readonly=True)
    event_begin_date = fields.Datetime(string="Event Start Date", related='event_id.date_begin', readonly=True)
    event_end_date = fields.Datetime(string="Event End Date", related='event_id.date_end', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', related='event_id.company_id',
                                 store=True, readonly=True, states={'draft': [('readonly', False)]})
    attendee_id = fields.Many2one('event.registration', required=True, string="Attendee")
    event_sessions_count = fields.Integer(related='event_id.sessions_count', readonly=True)
    state = fields.Selection([('draft', 'Unconfirmed'), ('cancel', 'Cancelled'),
                              ('open', 'Confirmed'), ('done', 'Attended')],
                             string='Status', default='draft', readonly=True, copy=False, track_visibility='onchange')

    # @api.multi
    # @api.constrains('event_id', 'session_id', 'state')
    # def _check_seats_limit(self):
    #     for registration in self.filtered('session_id'):
    #         if (registration.session_id.seats_availability == 'limited' and
    #                 registration.session_id.seats_available < 1 and
    #                 registration.state == 'open'):
    #             raise ValidationError(
    #                 _('No more seats available for this event.'))
    #
    # @api.multi
    # def confirm_registration(self):
    #     for reg in self:
    #         if not reg.event_id.session_ids:
    #             super(EventSessionAttend, reg).confirm_registration()
    #         reg.state = 'open'
    #         onsubscribe_schedulers = \
    #             reg.session_id.event_mail_ids.filtered(
    #                 lambda s: s.interval_type == 'after_sub')
    #         onsubscribe_schedulers.execute()
    #
    @api.one
    @api.constrains('event_id', 'state')
    def _check_seats_limit(self):
        if self.event_id.seats_availability == 'limited' and self.event_id.seats_max and self.event_id.seats_available < (
                1 if self.state == 'draft' else 0):
            raise ValidationError(_('No more seats available for this event.'))

    @api.multi
    def _check_auto_confirmation(self):
        if self._context.get('registration_force_draft'):
            return False
        if any(registration.event_id.state != 'confirm' or
               not registration.event_id.auto_confirm or
               (not registration.event_id.seats_available and registration.event_id.seats_availability == 'limited') for
               registration in self):
            return False
        return True

    @api.model
    def create(self, vals):
        registration = super(EventSessionAttend, self).create(vals)
        if registration._check_auto_confirmation():
            registration.sudo().confirm_registration()
        return registration

    @api.model
    def _prepare_attendee_values(self, registration):
        """ Method preparing the values to create new attendees based on a
        sale order line. It takes some registration data (dict-based) that are
        optional values coming from an external input like a web page. This method
        is meant to be inherited in various addons that sell events. """
        partner_id = registration.pop('partner_id', self.env.user.partner_id)
        event_id = registration.pop('event_id', False)
        data = {
            'name': registration.get('name', partner_id.name),
            'phone': registration.get('phone', partner_id.phone),
            'email': registration.get('email', partner_id.email),
            'partner_id': partner_id.id,
            'event_id': event_id and event_id.id or False,
        }
        data.update({key: registration[key] for key in registration.keys() if key in self._fields})
        return data

    @api.one
    def do_draft(self):
        self.state = 'draft'

    @api.one
    def confirm_registration(self):
        self.state = 'open'

        # auto-trigger after_sub (on subscribe) mail schedulers, if needed
        onsubscribe_schedulers = self.event_id.event_mail_ids.filtered(
            lambda s: s.interval_type == 'after_sub')
        onsubscribe_schedulers.execute()

    @api.one
    def button_reg_close(self):
        """ Close Registration """
        today = fields.Datetime.now()
        if self.event_id.date_begin <= today:
            self.write({'state': 'done', 'date_closed': today})
        else:
            raise UserError(_("You must wait for the starting day of the event to do this action."))

    @api.one
    def button_reg_cancel(self):
        self.state = 'cancel'

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id:
            contact_id = self.partner_id.address_get().get('contact', False)
            if contact_id:
                contact = self.env['res.partner'].browse(contact_id)
                self.name = contact.name or self.name
                self.email = contact.email or self.email
                self.phone = contact.phone or self.phone

    @api.multi
    def message_get_suggested_recipients(self):
        recipients = super(EventSessionAttend, self).message_get_suggested_recipients()
        try:
            for attendee in self:
                if attendee.partner_id:
                    attendee._message_add_suggested_recipient(recipients, partner=attendee.partner_id,
                                                              reason=_('Customer'))
                elif attendee.email:
                    attendee._message_add_suggested_recipient(recipients, email=attendee.email,
                                                              reason=_('Customer Email'))
        except AccessError:  # no read access rights -> ignore suggested recipients
            pass
        return recipients

    @api.multi
    def action_send_badge_email(self):
        """ Open a window to compose an email, with the template - 'event_badge'
            message loaded by default
        """
        self.ensure_one()
        template = self.env.ref('event.event_registration_mail_template_badge')
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        ctx = dict(
            default_model='event.registration',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def get_date_range_str(self):
        self.ensure_one()
        today = fields.Datetime.from_string(fields.Datetime.now())
        event_date = fields.Datetime.from_string(self.event_begin_date)
        diff = (event_date.date() - today.date())
        if diff.days == 0:
            return _('Today')
        elif diff.days == 1:
            return _('Tomorrow')
        elif event_date.isocalendar()[1] == today.isocalendar()[1]:
            return _('This week')
        elif today.month == event_date.month:
            return _('This month')
        elif event_date.month == (today + relativedelta(months=+1)):
            return _('Next month')
        else:
            return format_tz(self.env, self.event_begin_date, tz='UTC', format='%Y%m%dT%H%M%SZ')
