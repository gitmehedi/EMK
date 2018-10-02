# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventRoom(models.Model):
    _name = 'event.room'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char('Room Name', required=True, translate=True, track_visibility='onchange')
    max_seat = fields.Integer(string='Max Seat', required=True, track_visibility='onchange')
    min_seat = fields.Integer(string='Min Seat', required=True, track_visibility='onchange')
    status = fields.Boolean(default=True, track_visibility='onchange')

    event_count = fields.Integer(string="No of Events", compute='event_count_calculation')

    @api.multi
    def event_count_calculation(self):
        for records in self:
            events = self.env['event.event'].search([('state', '=', 'done')])
            records.event_count = len(events)

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise Exception(_('Name should not be duplicate.'))
