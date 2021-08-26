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

    @http.route(['/event/<model("event.event"):event>/registration/new'], type='json', auth="public", methods=['POST'],
                website=True)
    def registration_new(self, event, **post):
        tickets = self._process_tickets_details(post)
        if not tickets:
            return False
        return request.env['ir.ui.view'].render_template("website_event.registration_attendee_details",
                                                         {'tickets': tickets, 'event': event})

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
                                                         {'tickets': tickets, 'event': event, 'vals': vals})

    # @http.route(['/event/<model("event.event"):event>/registration/confirm'], type='http', auth="public",
    #             methods=['POST'], website=True)
    # def registration_confirm(self, event, **post):
    #     Attendees = request.env['event.registration']
    #     registrations = self._process_registration_details(post)
    #
    #     for registration in registrations:
    #         registration['event_id'] = event
    #         Attendees += Attendees.sudo().create(
    #             Attendees._prepare_attendee_values(registration))
    #         if Attendees:
    #             mail_ins = request.env['event.registration'].sudo()
    #
    #             event_reg = {
    #                 'template': 'event_management.event_confirmation_registration',
    #                 'email_to': Attendees['email']
    #             }
    #
    #             mail_ins.mailsend(event_reg)
    #
    #     return request.render("website_event.registration_complete", {'attendees': Attendees.sudo(), 'event': event})
