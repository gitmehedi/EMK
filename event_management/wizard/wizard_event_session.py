# -*- coding: utf-8 -*-


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from pytz import timezone, utc


class WizardEventSession(models.TransientModel):
    _name = "wizard.event.session.inherit"
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
