# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventSession(models.Model):
    _inherit = 'event.session'

    # registration_ids = fields.One2many('event.session.attend', 'session_id', string='Attendees')


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
