# -*- coding: utf-8 -*-


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from pytz import timezone, utc


class WizardEventSessionModel(models.TransientModel):
    _inherit = "wizard.event.session"


    @api.multi
    def action_generate_sessions(self):
        """Here's where magic is triggered"""
        weekdays = self.weekdays()
        if not any(weekdays):
            raise ValidationError(_("You must select at least one weekday"))
        if self.delete_existing_sessions:
            self.event_id.session_ids.unlink()
        self.generate_sessions()

        active_id = self.env.context['active_id']
        session = self.env['event.session'].search([('event_id', '=', active_id)])
        for ses in session:
            for rec in self.event_id.registration_ids:
                ses.attendee_ids.create({'session_id': ses.id, 'attendee_id': rec.id})
