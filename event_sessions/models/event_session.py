# -*- coding: utf-8 -*-
# Copyright 2017 David Vidal<david.vidal@tecnativa.com>
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from locale import setlocale, LC_ALL


class EventSession(models.Model):
    _name = 'event.session'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'event_id desc'
    _description = 'Event session'

    seats_min = fields.Integer(string="Min Seats")
    seats_max = fields.Integer(string="Max Seats")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(comodel_name='res.company', related='event_id.company_id', store=True, )
    event_id = fields.Many2one(comodel_name='event.event', string='Event', ondelete="cascade")
    seats_availability = fields.Selection([('limited', 'Limited'), ('unlimited', 'Unlimited')], 'Max Attendees',
                                          required=True, default='unlimited', )
    date_tz = fields.Selection(string='Timezone', related="event_id.date_tz", )
    date_begin = fields.Datetime(string="Session Start Date", required=True,
                                 default=lambda self: self.event_id.date_begin, )
    date_end = fields.Datetime(string="Session Date End", required=True, default=lambda self: self.event_id.date_end, )
    date_end = fields.Datetime(string="Last da Date End", required=True, default=lambda self: self.event_id.date_end, )

    registration_ids = fields.One2many(comodel_name='event.session.attend', inverse_name='session_id',
                                       string='Attendees', state={'done': [('readonly', True)]}, )
    event_mail_ids = fields.One2many(comodel_name='event.mail', inverse_name='session_id', string='Mail Schedule',
                                     copy=True)
    name = fields.Char(string='Session', required=True, compute="_compute_name", store=True, default='/', )
    date_begin_located = fields.Datetime(string='Start Date Located', compute='_compute_date_begin_located', )
    date_end_located = fields.Datetime(string='End Date Located', compute='_compute_date_end_located', )
    seats_reserved = fields.Integer(string='Reserved Seats', store=True, readonly=True, compute='_compute_seats', )
    seats_available = fields.Integer(oldname='register_avail', string='Available Seats', store=True, readonly=True,
                                     compute='_compute_seats')
    seats_unconfirmed = fields.Integer(oldname='register_prospect', string='Unconfirmed Seat Reservations', store=True,
                                       readonly=True, compute='_compute_seats')
    seats_used = fields.Integer(oldname='register_attended', string='No of Participants', store=True, readonly=True,
                                compute='_compute_seats')
    seats_expected = fields.Integer(string='No of Expected Attendees', readonly=True, compute='_compute_seats',
                                    store=True)
    seats_available_expected = fields.Integer(string='Available Expected Seats', readonly=True,
                                              compute='_compute_seats', store=True)
    seats_available_pc = fields.Float(string='Full %', readonly=True, compute='_compute_seats', )

    event_task_ids = fields.One2many('event.task.list', 'session_id', string="Event Tasks")
    event_book_ids = fields.One2many('event.room.book', 'session_id', string="Event Booking")

    state = fields.Selection([('unconfirmed', 'Unconfirmed'), ('confirmed', 'Confirmed'), ('done', 'Done')],
                             default='unconfirmed', string="State", track_visibility='onchange')

    @api.multi
    @api.depends('date_begin', 'date_end')
    def _compute_name(self):
        setlocale(LC_ALL, locale=(self.env.lang, 'UTF-8'))
        for session in self:
            if not (session.date_begin and session.date_end):
                session.name = '/'
                continue
            date_begin = fields.Datetime.from_string(
                session.date_begin_located)
            date_end = fields.Datetime.from_string(session.date_end_located)
            dt_format = '%A %m/%d/%y %H:%M'
            name = date_begin.strftime(dt_format)
            if date_begin.date() == date_end.date():
                dt_format = '%H:%M'
            name += " - " + date_end.strftime(dt_format)
            session.name = name.capitalize()

    def _session_mails_from_template(self, event_id, mail_template=None):
        vals = [(6, 0, [])]
        if not mail_template:
            mail_template = self.env['ir.values'].get_default(
                'event.config.settings', 'event_mail_template_id')
            if not mail_template:
                # Not template scheduler defined in event settings
                return vals
        if isinstance(mail_template, int):
            mail_template = self.env['event.mail.template'].browse(
                mail_template)
        for scheduler in mail_template.scheduler_template_ids:
            vals.append((0, 0, {
                'event_id': event_id,
                'interval_nbr': scheduler.interval_nbr,
                'interval_unit': scheduler.interval_unit,
                'interval_type': scheduler.interval_type,
                'template_id': scheduler.template_id.id,
            }))
        return vals

    @api.multi
    def name_get(self):
        """Redefine the name_get method to show the event name with the event
        session.
        """
        res = []
        for item in self:
            res.append((item.id, "[%s] %s" % (item.event_id.name, item.name)))
        return res

    @api.model
    def create(self, vals):
        if not vals.get('event_mail_ids', False):
            vals.update({
                'event_mail_ids':
                    self._session_mails_from_template(vals['event_id'])
            })
        return super(EventSession, self).create(vals)

    @api.multi
    @api.depends('seats_max', 'registration_ids.state')
    def _compute_seats(self):
        """Determine reserved, available, reserved but unconfirmed and used
        seats by session.
        """
        # aggregate registrations by event session and by state
        if len(self.ids) > 0:
            state_field = {
                'draft': 'seats_unconfirmed',
                'open': 'seats_reserved',
                'done': 'seats_used',
            }
            result = self.env['event.session.attend'].read_group(
                [('session_id', 'in', self.ids), ('state', 'in', ['draft', 'open', 'done'])], ['state', 'session_id'],
                ['session_id', 'state'], lazy=False)
            for res in result:
                session = self.browse(res['session_id'][0])
                session[state_field[res['state']]] += res['__count']
        # compute seats_available
        for session in self:
            if session.seats_max > 0:
                session.seats_available = session.seats_max - (
                        session.seats_reserved + session.seats_used)
            session.seats_expected = (
                    session.seats_unconfirmed + session.seats_reserved +
                    session.seats_used)
            session.seats_available_expected = (
                    session.seats_max - session.seats_expected)
            if session.seats_max > 0:
                session.seats_available_pc = (
                        session.seats_expected * 100 / float(session.seats_max))

    @api.multi
    @api.depends('date_tz', 'date_begin')
    def _compute_date_begin_located(self):
        for session in self.filtered('date_begin'):
            self_in_tz = session.with_context(
                tz=(session.date_tz or 'UTC')
            )
            date_begin = fields.Datetime.from_string(session.date_begin)
            session.date_begin_located = fields.Datetime.to_string(
                fields.Datetime.context_timestamp(self_in_tz, date_begin),
            )

    @api.multi
    @api.depends('date_tz', 'date_end')
    def _compute_date_end_located(self):
        for session in self.filtered('date_end'):
            self_in_tz = session.with_context(
                tz=(session.date_tz or 'UTC')
            )
            date_end = fields.Datetime.from_string(session.date_end)
            session.date_end_located = fields.Datetime.to_string(
                fields.Datetime.context_timestamp(self_in_tz, date_end),
            )

    @api.onchange('event_id')
    def onchange_event_id(self):
        self.update({
            'seats_min': self.event_id.seats_min,
            'seats_max': self.event_id.seats_max,
            'seats_availability': self.event_id.seats_availability,
            'date_begin': self.event_id.date_begin,
            'date_end': self.event_id.date_end,
        })

    @api.multi
    @api.constrains('seats_max', 'seats_available')
    def _check_seats_limit(self):
        for session in self:
            if (session.seats_availability == 'limited' and
                    session.seats_max and session.seats_available < 0):
                raise ValidationError(
                    _('No more available seats for this session.'))

    @api.multi
    @api.constrains('date_begin', 'date_end')
    def _check_dates(self):
        for session in self:
            if (self.event_id.date_end < session.date_begin or
                    session.date_begin < self.event_id.date_begin or
                    self.event_id.date_begin > session.date_end or
                    session.date_end > self.event_id.date_end):
                raise ValidationError(
                    _("Session date is out of this event dates range")
                )

    @api.multi
    @api.constrains('date_begin', 'date_end')
    def _check_zero_duration(self):
        for session in self:
            if session.date_begin == session.date_end:
                raise ValidationError(
                    _("Ending and starting time can't be the same!")
                )

    @api.multi
    def button_open_registration(self):
        """Opens session registrations"""
        self.ensure_one()
        action = self.env.ref('event_sessions.action_event_session_attend').read()[0]
        action['domain'] = [('id', 'in', self.registration_ids.ids)]
        action['context'] = {
            'default_event_id': self.event_id.id,
            'default_session_id': self.id,
        }
        return action

    @api.multi
    def act_confirmed(self):
        if self.state == 'unconfirmed':
            self.state = 'confirmed'

    @api.multi
    def act_unconfirmed(self):
        if self.state == 'confirmed':
            self.state = 'unconfirmed'

    @api.multi
    def act_done(self):
        if self.state == 'confirmed':
            self.state = 'done'

    @api.one
    def button_assign(self):
        self.write({'state': 'assign'})

    @api.one
    def add_attendee(self):
        if self.state == 'unconfirmed':
            attendee = set(self.event_id.registration_ids.ids) - set([val.attendee_id.id for val in self.registration_ids])
            for rec in list(attendee):
                ses_reg = {
                    'session_id': self.id,
                    'event_id': self.event_id.id,
                    'attendee_id': rec,
                }
                self.registration_ids.create(ses_reg)

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['unconfirmed', 'confirmed'])]


class EventRoomBook(models.Model):
    _inherit = 'event.room.book'

    session_id = fields.Many2one('event.session', string='Session', ondelete='cascade')


class EventTaskList(models.Model):
    _inherit = 'event.task.list'

    session_id = fields.Many2one('event.session', string='Session', ondelete='cascade')
