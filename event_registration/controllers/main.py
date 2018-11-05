# -*- coding: utf-8 -*-

import babel.dates
import re
import werkzeug
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import fields, http, _
from odoo.addons.website.models.website import slug
from odoo.http import request
from odoo.addons.website_event.controllers.main import WebsiteEventController


class WebsiteRegistration(WebsiteEventController):

    @http.route()
    def registration_new(self, event, **post):
        super(WebsiteRegistration, self).registration_new(event)
        tickets = self._process_tickets_details(post)
        if not tickets:
            return False

        vals = {
            'professions': http.request.env['attendee.profession'].sudo().search([('status', '=', True)]),
            'gender_ids': {'male': 'Male', 'female': 'Female'},
        }
        return request.env['ir.ui.view'].render_template("website_event.registration_attendee_details",
                                                         {'tickets': tickets, 'event': event,
                                                          'vals': vals})
