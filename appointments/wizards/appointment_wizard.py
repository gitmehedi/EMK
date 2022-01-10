import time
import re
from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
import dateutil.parser
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError


class AppointmentWizard(models.TransientModel):
    _name = 'appointment.wizard'

    appointment_date = fields.Date('Appointment Date', required=True, track_visibility="onchange")
    topic_id = fields.Many2one('appointment.topics', string="Topics", required=True, track_visibility='onchange')
    contact_id = fields.Many2one('appointment.contact', string="Appointee", required=True, track_visibility='onchange')
    timeslot_id = fields.Many2one('appointment.timeslot', string="Time", required=True, track_visibility='onchange')
    meeting_room_id = fields.Many2one('appointment.meeting.room', string="Meeting Room", required=True, track_visibility='onchange')

    @api.onchange('topic_id')
    def onchange_topic_id(self):
        res = {}
        self.contact_id = 0
        if self.topic_id:
            res['domain'] = {
                'contact_id': [('id', 'in', self.topic_id.contact_ids.ids)],
            }
        return res

    @api.onchange('contact_id')
    def onchange_contact_id(self):
        res = {}
        self.timeslot_id = 0
        if self.contact_id:
            res['domain'] = {
                'timeslot_id': [('id', 'in', self.contact_id.timeslot_ids.ids)],
            }
        return res

    @api.onchange('appointment_date', 'contact_id')
    def onchange_appointment_date(self):
        res = {}
        day = ''
        current_time = ''
        today = datetime.today()
        self.timeslot_id = 0
        slots = []
        if self.appointment_date:
            appdate = datetime.strptime(self.appointment_date, "%Y-%m-%d")
            day = datetime.strftime(appdate, '%A')
            now = datetime.now() + timedelta(hours=6)
            current_time = now.strftime("%H:%M")

        appointment_slots = self.env['appointment.appointment'].search([('contact_id', '=', self.contact_id.id),
                                                                        ('appointment_date', '=',
                                                                         self.appointment_date),
                                                                        ('state', 'in',
                                                                         ['draft', 'confirm', 'approve'])])

        app_slots = [val.timeslot_id.id for val in appointment_slots]

        contact_slots = self.env['appointment.contact'].search([('id', '=', self.contact_id.id),
                                                                ('state', '=', 'approve')])

        if self.appointment_date == datetime.strftime(today, "%Y-%m-%d"):
            for slot in contact_slots.timeslot_ids:
                slot_time_format = '{0:02.0f}:{1:02.0f}'.format(*divmod(slot.end_time * 60, 60))
                if (slot.id not in app_slots) and (slot.day == day.lower()) and slot_time_format >= current_time:
                    slots.append(slot.id)
        else:
            for slot in contact_slots.timeslot_ids:
                if (slot.id not in app_slots) and (slot.day == day.lower()):
                    slots.append(slot.id)
        if slots:
            res['domain'] = {'timeslot_id': [('id', 'in', slots)]}
        else:
            res['domain'] = {'timeslot_id': [('id', '=', -1)]}
        return res

    @api.onchange('timeslot_id')
    def onchange_timeslot_id(self):
        res = {}
        self.meeting_room_id = 0
        if self.timeslot_id:
            appointment = self.env['appointment.appointment'].search([('timeslot_id', '=', self.timeslot_id.id),
                                                                      ('appointment_date', '=',
                                                                       self.appointment_date),
                                                                      ('state', 'in', ['draft',
                                                                                       'confirm', 'approve'])])

            meeting_room = self.env['appointment.meeting.room'].search(
                [('id', 'not in', appointment.meeting_room_id.ids
                  ), ('state', '=', 'approve')])

            if meeting_room:
                res['domain'] = {'meeting_room_id': [('id', 'in', meeting_room.ids)]}
            else:
                res['domain'] = {'meeting_room_id': [('id', '=', -1)]}
            return res

    @api.one
    @api.constrains('appointment_date')
    def validate_appointment_date(self):
        if self.appointment_date:
            app_date = datetime.strptime(self.appointment_date, '%Y-%m-%d')
            curr_date = dateutil.parser.parse(fields.Date.today())
            if app_date < curr_date:
                raise ValidationError(_("Appointment date cannot be past date from current date"))

    def act_change_date(self):
        active_id = self._context['active_id']
        record = self.env['appointment.appointment'].search([('id', '=', active_id)])

        if record:
            template_id = self.env.ref('appointments.mail_template_appointment_reschedule_emk').id
            template = self.env['mail.template'].browse(template_id)
            template.send_mail(active_id, force_send=True)

            res = {
                'appointment_date': self.appointment_date,
                'topic_id': self.topic_id.id,
                'contact_id': self.contact_id.id,
                'timeslot_id': self.timeslot_id.id,
                'meeting_room_id': self.meeting_room_id.id,
            }

            record.write(res)





