# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventEvent(models.Model):
    _inherit = 'event.event'

    event_type_id = fields.Many2one('event.type', string='Category',
                                    readonly=False, states={'done': [('readonly', True)]}, required=True)
    event_book_ids = fields.One2many('event.room.book', 'event_id', string='Event Room')
    total_seat_available = fields.Integer(string="Total Seat Available", compute='compute_total_seat')

    @api.depends('event_book_ids')
    def compute_total_seat(self):
        for record in self:
            record.total_seat_available=sum([rec.seat_no for rec in record.event_book_ids])
