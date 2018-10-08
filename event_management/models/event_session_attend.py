# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventSessionAttend(models.Model):
    _inherit = 'event.session.attend'

    registration_ids = fields.One2many(
        comodel_name='event.session.attend',
        inverse_name='session_id',
        string='Attendees',
        state={'done': [('readonly', True)]},
    )

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
