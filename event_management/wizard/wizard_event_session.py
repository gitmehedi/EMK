# -*- coding: utf-8 -*-


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from pytz import timezone, utc


class WizardEventSessionModel(models.TransientModel):
    _inherit = "wizard.event.session"
    # _name = "wizard.event.session.model"

    @api.multi
    def action_generate_sessions(self):
        active_id =self.env.context['active_id']
        super(WizardEventSessionModel,self).action_generate_sessions()
        session=self.env['event.session'].search([('event_id', '=', active_id)])
        for ses in session:
            for rec in self.event_id.registration_ids:
                self

        return False
        weekdays = self.weekdays()
        if not any(weekdays):
            raise ValidationError(_("You must select at least one weekday"))
        if self.delete_existing_sessions:
            self.event_id.session_ids.unlink()
        self.generate_sessions()
