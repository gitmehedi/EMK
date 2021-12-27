# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import http, _
from odoo.http import request

DATE_FORMAT = "%Y-%m-%d"


class WebsiteAppointmentReservation(http.Controller):
    # @http.route(['/event/<model("event.event"):event>/registration/new'], type='json', auth="public", methods=['POST'],
    #             website=True)
    # def registration_new(self, event, **post):
    #     tickets = self._process_tickets_details(post)
    #     if not tickets:
    #         return False
    #     return request.env['ir.ui.view'].render_template("website_event.registration_attendee_details",
    #                                                      {'tickets': tickets, 'event': event})
    #
    # @http.route()
    # def registration_new(self, event, **post):
    #     super(WebsiteAppointmentReservation, self).registration_new(event)
    #     tickets = self._process_tickets_details(post)
    #     if not tickets:
    #         return False
    #
    #     vals = {
    #         'professions': http.request.env['attendee.profession'].sudo().search([('status', '=', True)]),
    #         'gender_ids': http.request.env['res.gender'].sudo().search([('status', '=', True)], order='id asc'),
    #     }
    #     return request.env['ir.ui.view'].render_template("website_event.registration_attendee_details",
    #                                                      {'tickets': tickets, 'event': event, 'vals': vals})

    @http.route(['/appointment/reservation'], type='http', auth="public", website=True, methods=['GET', 'POST'])
    def appointment_reservation(self, **post):
        qctx = self.get_signup_context()
        token = request.params.get('token')
        # if token:
        #     event = request.env['event.reservation'].sudo().search([('reserv_token', '=', token), ('state', '=', 'draft')])
        #     if event:
        #         qctx['id'] = event.id
        #         qctx['event_name'] = event.event_name
        #         qctx['poc_id'] = event.poc_id.id
        #         qctx['org_id'] = event.org_id.id
        #         qctx['token'] = token
        #     if not event:
        #         return request.render('event_registration.event_reservation_expire')
        # else:
        #     return request.render('event_registration.event_reservation_expire')

        if request.httprequest.method == 'POST' and ('error' not in qctx):
            try:
                auth_data = self.post_events(qctx)
                if auth_data:
                    try:
                        return request.render('appointments.appointment_reservation_success')
                    except:
                        return request.render('appointments.appointment_reservation_success')
            except (WebsiteAppointmentReservation, AssertionError) as e:
                qctx['error'] = _("Could not create a new account.")

        qctx['name'] = None if 'name' not in qctx else qctx['name']
        qctx['topic_id'] = None if 'topic_id' not in qctx else int(qctx['topic_id'])
        qctx['contact_id'] = None if 'contact_id' not in qctx else int(qctx['contact_id'])
        qctx['timeslot_id'] = None if 'timeslot_id' not in qctx else int(qctx['timeslot_id'])
        qctx['type_id'] = None if 'type_id' not in qctx else int(qctx['type_id'])
        qctx['meeting_room_id'] = None if 'meeting_room_id' not in qctx else int(qctx['meeting_room_id'])
        qctx['description'] = None if 'description' not in qctx else qctx['description']
        qctx['appointment_date'] = None if 'appointment_date' not in qctx else datetime.strptime(
            qctx.get('appointment_date'), '%Y-%m-%d')
        qctx['first_name'] = None if 'first_name' not in qctx else qctx['first_name']
        qctx['last_name'] = None if 'last_name' not in qctx else qctx['last_name']
        qctx['gender_id'] = None if 'gender_id' not in qctx else int(qctx['gender_id'])
        qctx['date_of_birth'] = None if 'date_of_birth' not in qctx else datetime.strptime(qctx.get('date_of_birth'),
                                                                                           '%Y-%m-%d')
        qctx['phone'] = None if 'phone' not in qctx else int(qctx['phone'])
        qctx['street'] = None if 'street' not in qctx else qctx['street']
        qctx['street2'] = None if 'street2' not in qctx else qctx['street2']
        qctx['city'] = None if 'city' not in qctx else qctx['city']
        qctx['zipcode'] = None if 'zipcode' not in qctx else qctx['zipcode']
        qctx['country_id'] = None if 'country_id' not in qctx else int(qctx['country_id'])
        qctx['email'] = None if 'email' not in qctx else qctx['email']

        if 'topic_ids' not in qctx:
            qctx['topic_ids'] = self.generateDropdown('appointment.topics')

        if 'contact_ids' not in qctx:
            qctx['contact_ids'] = self.generateDropdown('appointment.contact')

        if 'timeslot_ids' not in qctx:
            qctx['timeslot_ids'] = self.generateDropdown('appointment.timeslot')

        if 'type_ids' not in qctx:
            qctx['type_ids'] = self.generateDropdown('appointment.type')

        if 'meeting_room_ids' not in qctx:
            qctx['meeting_room_ids'] = self.generateDropdown('appointment.meeting.room')

        if 'country_ids' not in qctx:
            qctx['country_ids'] = self.generateDropdown('res.country')

        if 'gender_ids' not in qctx:
            qctx['gender_ids'] = self.generateDropdown('res.gender')

        return request.render("appointments.appointment_reservation", qctx)

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
            data['state'] = 'draft'

        assert values.values(), "The form was not properly filled in."

        return request.env['appointment.appointment'].sudo().post_appointments(data, values.get('token'))

    def authorized_fields(self):
        return (
            'id',
            'token',
            'name',
            'topic_id',
            'contact_id',
            'timeslot_id',
            'type_id',
            'meeting_room_id',
            'description',
            'appointment_date',
            'first_name',
            'last_name',
            'gender_id',
            'appointment_date',
            'date_of_birth',
            'phone',
            'street',
            'street2',
            'zipcode',
            'city',
            'country_id',
            'email',
        )

    @http.route(['/appointment/contacts'], type='json', website=True, auth='public', method=['POST'])
    def get_contacts(self, **post):
        topic_id = int(post['topic_id'])
        topics = request.env['appointment.topics'].sudo().search([('id', '=', topic_id)])
        contacts = [{'id': contact.id, 'name': contact.name} for contact in topics.contact_ids]
        return {
            'contacts': contacts
        }

    @http.route(['/appointment/available-slot'], type='json', website=True, auth='public', method=['POST'])
    def get_available_slots(self, **post):
        appointment_date = post['appointment_date']
        contact_id = int(post['contact_id'])
        day_name = datetime.strptime(appointment_date, DATE_FORMAT).strftime('%A')

        appointment_slots = request.env['appointment.appointment'].sudo().search([('contact_id', '=', contact_id),
                                                                                  ('appointment_date', '=',
                                                                                   appointment_date),
                                                                                  ('state', 'in',
                                                                                   ['draft', 'confirm', 'done'])])
        app_slots = [val.timeslot_id.id for val in appointment_slots]
        contact_slots = request.env['appointment.contact'].sudo().search(
            [('id', '=', contact_id), ('status', '=', True)])
        slots = []
        for slot in contact_slots.timeslot_ids:
            if (slot.id not in app_slots) and (day_name.lower() == slot.day):
                slots.append({'id': slot.id, 'name': slot.name})
        return {
            'slots': slots
        }
