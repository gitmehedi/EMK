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

            res={
                'appointment_date': self.appointment_date,
                'topic_id': self.topic_id.id,
                'contact_id': self.contact_id.id,
                'timeslot_id': self.timeslot_id.id,
            }

            record.write(res)

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
        if self.appointment_date:
            appdate = datetime.strptime(self.appointment_date, "%Y-%m-%d")
            day = datetime.strftime(appdate, '%A')
            timeslot_ids = self.env['appointment.timeslot'].search(
                [('day', '=', day.lower()), ('id', 'in', self.contact_id.timeslot_ids.ids)])

            if timeslot_ids:
                res['domain'] = {
                    'timeslot_id': [('id', 'in', timeslot_ids.ids)],

                }
        return res



