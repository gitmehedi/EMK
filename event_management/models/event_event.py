# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventEvent(models.Model):
    _inherit = 'event.event'
    _order = 'id desc'

    organizer_id = fields.Many2one('res.partner', string='Organizer Name', domain=[('is_organizer', '=', True)],
                                   default=False, required=True, readonly=False, states={'done': [('readonly', True)]})
    total_seat_available = fields.Integer(string="Total Seat Available", compute='compute_total_seat')
    event_book_ids = fields.One2many('event.room.book', 'event_id', string='Event Rooms', readonly=False,
                                     states={'done': [('readonly', True)]})
    event_task_ids = fields.One2many('event.task.list', 'event_id', string='Event Tasks', readonly=False,
                                     states={'done': [('readonly', True)]})
    date_begin = fields.Datetime(string='Start Date', required=True,
                                 track_visibility='onchange',
                                 states={'confirm': [('readonly', True)], 'done': [('readonly', True)]})
    payment_type = fields.Selection([('free', 'Free'), ('paid', 'Paid')], required=True, default='free', string='Type',
                                    readonly=False, states={'done': [('readonly', True)]})
    mode_of_payment = fields.Selection([('cash', 'Cash'), ('bank', 'Bank')], required=True, default='cash',
                                       readonly=False, states={'done': [('readonly', True)]},
                                       string='Mode Of Payment')
    paid_amount = fields.Float(string='Paid Amount', digits=(12, 2), readonly=False,
                               states={'done': [('readonly', True)]})
    refundable_amount = fields.Float(string='Refundable Amount', digits=(12, 2), readonly=False,
                                     states={'done': [('readonly', True)]})
    rules_regulation = fields.Html(string='Rules and Regulation', readonly=False, states={'done': [('readonly', True)]})
    date_of_payment = fields.Date(string="Expected Date for Payment", readonly=False,
                                  states={'done': [('readonly', True)]})
    notes = fields.Html(string="Comments/Notes", readonly=False, states={'done': [('readonly', True)]})
    ref_reservation = fields.Char(string="Reservation Reference", readonly=False, states={'done': [('readonly', True)]})
    image_medium = fields.Binary(string='Medium-sized photo', attachment=True)
    participating_amount = fields.Integer(string="Participation Amount", readonly=True,
                                          states={'confirm': [('readonly', False)]})

    @api.depends('event_book_ids')
    def compute_total_seat(self):
        for record in self:
            record.total_seat_available = sum([rec.seat_no for rec in record.event_book_ids])

    @api.multi
    @api.constrains('date_begin')
    def _check_date_begin(self):
        dt_now = fields.datetime.now()
        date_begin = datetime.datetime.strptime(self.date_begin, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(minutes=1)
        if date_begin < dt_now:
            raise ValidationError(_("Event start date cannot be past date from current date"))

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise ValidationError(_('[DUPLICATE] Name already exist, choose another.'))

    @api.one
    def button_done(self):
        if self.state == 'confirmed':
            # self.event_book_ids
            # self.registration_ids
            # self.event_book_ids
            # self.event_task_ids
            # self.session_ids

            self.state = 'done'

        # event_book_ids

    @api.multi
    def unlink(self):
        for event in self:
            if event.state == 'done':
                raise ValidationError(_('You cannot delete a record which is not in draft state!'))
        return super(EventEvent, self).unlink()

    @api.multi
    @api.depends('name', 'date_begin', 'date_end')
    def name_get(self):
        result = []
        for event in self:
            date_begin = fields.Datetime.from_string(event.date_begin)
            date_end = fields.Datetime.from_string(event.date_end)
            dates = [fields.Date.to_string(fields.Datetime.context_timestamp(event, dt)) for dt in
                     [date_begin, date_end] if dt]
            dates = sorted(set(dates))
            result.append((event.id, '%s [%s]' % (event.name, ' - '.join(dates))))
        return result

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['confirm', 'draft'])]


class EventRegistration(models.Model):
    _name = 'event.registration'
    _inherit = ['event.registration', 'mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'

    date_of_birth = fields.Date(string='Date of Birth', required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], required=True,
                              default='male', string='Gender')
    profession_id = fields.Many2one('attendee.profession', string='Profession', required=True, default=False)
    card_number = fields.Char(string='Card Number')

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['draft', 'open'])]


class AttendeeProfession(models.Model):
    _name = 'attendee.profession'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'
    _description = 'Attendee Profession'

    name = fields.Char(string='Profession', required=True)
    status = fields.Boolean(default=True)
