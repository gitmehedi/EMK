# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventSession(models.Model):
    _inherit = 'event.session'

    total_seat_available = fields.Integer(string="Total Seat Available", compute='compute_total_seat')
    event_book_ids = fields.One2many('event.room.book', 'event_id', string='Event Rooms')
    event_task_ids = fields.One2many('event.task.list', 'event_id', string='Event Tasks')
    event_type_id = fields.Many2one('event.type', string='Category',
                                    readonly=False, states={'done': [('readonly', True)]}, required=True)
    state = fields.Selection([('unconfirmed', 'Unconfirmed'), ('confirmed', 'Confirmed'), ('done', 'Done')],
                             default='unconfirmed', string="State", track_visibility='onchange')

    @api.depends('event_book_ids')
    def compute_total_seat(self):
        for record in self:
            record.total_seat_available = sum([rec.seat_no for rec in record.event_book_ids])

    @api.one
    def register_participant(self):
        return True

    @api.one
    def act_unconfirmed(self):
        return True

    @api.one
    def act_confirmed(self):
        return True

    @api.one
    def act_done(self):
        return True
