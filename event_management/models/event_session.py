# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventSession(models.Model):
    _inherit = 'event.session'

    attendee_ids = fields.One2many('event.session.attend', 'session_id', string='Attendees')
    state = fields.Selection([('unconfirmed', 'Unconfirmed'), ('confirmed', 'Confirmed'), ('done', 'Done')],
                             default='unconfirmed', string="State", track_visibility='onchange')

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
