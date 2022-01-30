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
from odoo.addons.opa_utility.helper.utility import Utility as utility


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
            'gender_ids': http.request.env['res.gender'].sudo().search([('status', '=', True)], order='id asc'),
        }
        return request.env['ir.ui.view'].render_template("website_event.registration_attendee_details",
                                                         {'tickets': tickets, 'event': event, 'vals': vals})

    @http.route(['/event/event-reservation/register'], type='http', auth="public", website=True)
    def event_reservation(self, **post):
        qctx = self.get_signup_context()
        token = request.params.get('token')
        if token:
            event = request.env['event.reservation'].sudo().search(
                [('reserv_token', '=', token), ('state', '=', 'draft')])
            if event:
                qctx['id'] = event.id
                qctx['event_name'] = event.event_name
                qctx['poc_id'] = event.poc_id.id
                qctx['org_id'] = event.org_id.id
                qctx['token'] = token
            if not event:
                return request.render('event_registration.event_reservation_expire')
        else:
            return request.render('event_registration.event_reservation_expire')

        if request.httprequest.method == 'POST' and ('error' not in qctx):
            try:
                auth_data = self.post_events(qctx)
                if auth_data:
                    try:
                        return request.render('event_registration.event_reservation_success')
                    except:
                        return request.render('event_registration.event_reservation_success')
            except (WebsiteRegistration, AssertionError), e:
                qctx['error'] = _("Could not create a new account.")

        qctx['event_name'] = None if 'event_name' not in qctx else qctx['event_name']
        qctx['poc_type_id'] = None if 'poc_type_id' not in qctx else int(qctx['poc_type_id'])
        qctx['facilities_ids'] = None if 'facilities_ids' not in qctx else int(qctx['facilities_ids'])
        qctx['event_type_id'] = None if 'event_type_id' not in qctx else int(qctx['event_type_id'])
        qctx['space_id'] = 'yes' if 'space_id' not in qctx else qctx['space_id']
        qctx['seats_available'] = 'limited' if 'seats_available' not in qctx else qctx['seats_available']
        qctx['total_session'] = None if 'total_session' not in qctx else qctx['total_session']
        qctx['request_date'] = None if 'request_date' not in qctx else qctx['request_date']
        qctx['start_date'] = None if 'start_date' not in qctx else qctx['start_date']
        qctx['end_date'] = None if 'end_date' not in qctx else qctx['end_date']
        qctx['last_date_reg'] = None if 'last_date_reg' not in qctx else qctx['last_date_reg']
        qctx['mode_of_payment'] = 'cash' if 'mode_of_payment' not in qctx else qctx['mode_of_payment']
        qctx['payment_type'] = 'paid' if 'payment_type' not in qctx else qctx['payment_type']
        qctx['date_of_payment'] = None if 'date_of_payment' not in qctx else qctx['date_of_payment']
        qctx['proposed_budget'] = None if 'proposed_budget' not in qctx else qctx['proposed_budget']
        qctx['paid_attendee'] = 'yes' if 'paid_attendee' not in qctx else qctx['paid_attendee']
        qctx['attendee_number'] = None if 'attendee_number' not in qctx else qctx['attendee_number']
        qctx['participating_amount'] = None if 'participating_amount' not in qctx else qctx['participating_amount']
        qctx['target_audience_group'] = 'paid' if 'target_audience_group' not in qctx else qctx['target_audience_group']
        qctx['target_age'] = None if 'target_age' not in qctx else qctx['target_age']
        qctx['outreach_plan'] = None if 'outreach_plan' not in qctx else qctx['outreach_plan']
        qctx['outreach_plan_other'] = None if 'outreach_plan_other' not in qctx else qctx['outreach_plan_other']
        qctx['snakes_required'] = 'yes' if 'snakes_required' not in qctx else qctx['snakes_required']
        qctx['description'] = None if 'description' not in qctx else qctx['description'].strip()
        qctx['rules_regulation'] = None if 'rules_regulation' not in qctx else qctx['rules_regulation'].strip()
        qctx['notes'] = None if 'notes' not in qctx else qctx['notes'].strip()
        qctx['purpose_of_event'] = None if 'purpose_of_event' not in qctx else qctx['purpose_of_event'].strip()

        if 'facilities_ids' not in qctx:
            qctx['facilities_ids'] = []
        else:
            qctx['facilities_ids'] = [int(val) for val in
                                               request.httprequest.form.getlist('facilities_ids')]

        if 'poc_ids' not in qctx:
            qctx['poc_ids'] = self.generateDropdown('res.partner')

        if 'poc_type_ids' not in qctx:
            qctx['poc_type_ids'] = self.generateDropdown('event.poc.type')

        if 'facilities' not in qctx:
            qctx['facilities'] = self.generateDropdown('event.service.type')

        if 'event_type_ids' not in qctx:
            qctx['event_type_ids'] = self.generateDropdown('event.type')

        if 'space_ids' not in qctx:
            qctx['space_ids'] = [('yes', 'Yes'), ('no', 'No')]

        if 'seats_available_ids' not in qctx:
            qctx['seats_available_ids'] = [('limited', 'Limited'), ('unlimited', 'Unlimited')]

        if 'payment_ids' not in qctx:
            qctx['payment_ids'] = [('cash', 'Cash'), ('bank', 'Bank'), ('bkash', 'bKash')]

        if 'payment_type_ids' not in qctx:
            qctx['payment_type_ids'] = [('paid', 'Paid'), ('free', 'Free')]

        if 'snakes_ids' not in qctx:
            qctx['snakes_ids'] = [('yes', 'Yes'), ('no', 'No')]

        if 'target_audience_group_ids' not in qctx:
            qctx['target_audience_group_ids'] = [('yes', 'Yes'), ('no', 'No')]

        if 'paid_attendee_ids' not in qctx:
            qctx['paid_attendee_ids'] = [('yes', 'Yes'), ('no', 'No')]

        if 'outreach_plan_ids' not in qctx:
            qctx['outreach_plan_ids'] = [('social_media', 'Social Media Promotions'),
                                         ('press_coverage', 'Press Coverage'),
                                         ('designing', 'Designing'),
                                         ('others', 'Others')]

        return request.render("event_registration.event_reservation", qctx)

    def get_signup_context(self):
        qctx = request.params.copy()
        qctx['baseurl'] = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return qctx

    def generateDropdown(self, model, status=False):
        data = []
        status = [('status', '=', True)] if status else []
        record = request.env[model].sudo().search(status, order='id ASC')
        for rec in record:
            if status:
                val = '_'.join((rec.name).strip().lower().split())
                data.append((val, rec.name))
            else:
                data.append((rec.id, rec.name))
        return data

    def post_events(self, values):
        data, error_fields = {}, []
        authorized_fields = self.authorized_fields()

        """ Shared helper that creates a res.partner out of a token """
        for field_name, field_value in values.items():
            if hasattr(field_value, 'filename'):
                field_name = field_name.rsplit('[', 1)[0]
                field_value.field_name = field_name
            elif field_name in authorized_fields:
                try:
                    data[field_name] = field_value
                except ValueError:
                    error_fields.append(field_name)

        if len(data) > 0:
            data['state'] = 'reservation'
            vals = [int(val) for val in request.httprequest.form.getlist('facilities_ids')]
            data['facilities_ids'] = [(6, 0, vals)]

        assert values.values(), "The form was not properly filled in."

        return request.env['event.reservation'].sudo().post_event_reservation(data, values.get('token'))

    def authorized_fields(self):
        return (
            'id',
            'token',
            'org_id',
            'event_name',
            'event_name',
            'poc_id',
            'poc_type_id',
            'facilities_ids',
            'event_type_id',
            'space_id',
            'seats_available',
            'total_session',
            'request_date',
            'start_date',
            'end_date',
            'last_date_reg',
            'mode_of_payment',
            'payment_type',
            'date_of_payment',
            'proposed_budget',
            'paid_attendee',
            'attendee_number',
            'participating_amount',
            'target_audience_group',
            'target_age',
            'outreach_plan',
            'outreach_plan_other',
            'snakes_required',
            'description',
            'rules_regulation',
            'notes',
            'purpose_of_event',
        )
