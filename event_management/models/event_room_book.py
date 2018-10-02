# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventRoomBook(models.Model):
    _name = 'event.room.book'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    event_id = fields.Many2one('event.event', string='Event', required=True)
    room_id = fields.Many2one('event.room', string='Event Room', required=True)
    seat_no = fields.Integer(related='room_id.max_seat', readonly="True", string="Available Seat")

    event_start = fields.Datetime(string='Event Start', required=True)
    event_stop = fields.Datetime(string='Event Stop', required=True)
    status = fields.Boolean(default=True, track_visibility='onchange')

    @api.onchange('room_id')
    def onchange_room(self):
        if self.room_id:
            data = self.search([('room_id', '=', self.room_id.id), ('event_start', '<=', self.event_id.date_begin),
                                ('event_stop', '>=', self.event_id.date_begin), '|',
                                ('event_start', '<=', self.event_id.date_end),
                                ('event_stop', '>=', self.event_id.date_end)])
            if len(data) > 0:
                raise UserError(
                    _('[{0}] room already book for another event, please choose another.'.format(self.room_id.name)))

            self.event_start = self.event_id.date_begin
            self.event_stop = self.event_id.date_end

    @api.constrains('room_id', 'event_start', 'event_stop')
    def check_room(self):
        data = self.search([('room_id', '=', self.room_id.id), ('event_start', '<=', self.event_id.date_begin),
                            ('event_stop', '>=', self.event_id.date_begin), '|',
                            ('event_start', '<=', self.event_id.date_end),
                            ('event_stop', '>=', self.event_id.date_end)])
        if len(data) > 1:
            raise UserError(
                _('[{0}] room already book for another event, please choose another.'.format(self.room_id.name)))
