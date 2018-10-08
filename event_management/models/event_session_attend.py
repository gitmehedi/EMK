# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventSessionAttend(models.Model):
    _name = 'event.session.attend'

    session_id = fields.Many2one('event.session', string='Session Name', required=True, ondelete='cascade')
    attendee_id = fields.Many2one('event.registration', string='Attendees', required=True)
    email = fields.Char(related='attendee_id.email', string='Email', readonly=True)
    phone = fields.Char(related='attendee_id.email', string='Phone', readonly=True)
    attend = fields.Boolean(default=False, string='Attend')
    state = fields.Selection([('draft', 'Unconfirmed'), ('cancel', 'Cancelled'),
                              ('open', 'Confirmed'), ('done', 'Attended')], string='Status', default='draft',
                             readonly=True, copy=False, track_visibility='onchange')

    @api.one
    def confirm_registration(self):
        self.state = 'open'

        # auto-trigger after_sub (on subscribe) mail schedulers, if needed
        onsubscribe_schedulers = self.event_id.event_mail_ids.filtered(
            lambda s: s.interval_type == 'after_sub')
        onsubscribe_schedulers.execute()

    @api.one
    def button_reg_close(self):
        """ Close Registration """
        today = fields.Datetime.now()
        if self.event_id.date_begin <= today:
            self.write({'state': 'done', 'date_closed': today})
        else:
            raise UserError(_("You must wait for the starting day of the event to do this action."))

    @api.one
    def button_reg_cancel(self):
        self.state = 'cancel'
