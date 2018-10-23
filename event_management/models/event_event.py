# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventEvent(models.Model):
    _inherit = 'event.event'

    organizer_id = fields.Many2one('res.partner', string='Organizer Name', domain=[('is_organizer', '=', True)],
                                   default=False, required=True)
    total_seat_available = fields.Integer(string="Total Seat Available", compute='compute_total_seat')
    event_book_ids = fields.One2many('event.room.book', 'event_id', string='Event Rooms')
    event_task_ids = fields.One2many('event.task.list', 'event_id', string='Event Tasks')
    date_begin = fields.Datetime(string='Start Date', required=True,
                                 track_visibility='onchange',
                                 states={'confirm': [('readonly', True)], 'done': [('readonly', True)]})

    payment_type = fields.Selection([('free', 'Free'), ('paid', 'Paid')], required=True, default='free', string='Type')
    mode_of_payment = fields.Selection([('cash', 'Cash'), ('bank', 'Bank')], required=True, default='cash',
                                       string='Mode Of Payment')
    paid_amount = fields.Float(string='Paid Amount', digits=(12, 2))
    refundable_amount = fields.Float(string='Refundable Amount', digits=(12, 2))
    rules_regulation = fields.Html(string='Rules and Regulation')
    date_of_payment = fields.Date(string="Expected Date for Payment")
    notes = fields.Html(string="Comments/Notes")
    ref_reservation = fields.Char(string="Reservation Reference")
    image_medium = fields.Binary(string='Medium-sized photo', attachment=True)

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


class EventRegistration(models.Model):
    _inherit = 'event.registration'
    _order = 'id desc'

    date_of_birth = fields.Date(string='Date of Birth', required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], required=True,
                              default='male', string='Gender')
    profession = fields.Char(string='Profession', required=True, default=False)
