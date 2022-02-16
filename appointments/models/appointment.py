import logging, re
from datetime import datetime,time,timedelta
import dateutil.parser
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.opa_utility.helper.utility import Utility,Message

_logger = logging.getLogger(__name__)


class Appointment(models.Model):
    _name = 'appointment.appointment'
    _description = "Appointment"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "id desc"

    @api.model
    def _get_required_date(self):
        return datetime.strftime(datetime.today(), DEFAULT_SERVER_DATETIME_FORMAT)

    name = fields.Char(string="Reference", readonly=True, copy=False, track_visibility='onchange')
    topic_id = fields.Many2one('appointment.topics', string="Topics", required=True, track_visibility='onchange')
    contact_id = fields.Many2one('appointment.contact', string="Appointer", required=True, track_visibility='onchange')
    timeslot_id = fields.Many2one('appointment.timeslot', string="Time", required=True, track_visibility='onchange')
    type_id = fields.Many2one('appointment.type', string="Appointment Type", required=True, track_visibility='onchange')
    meeting_room_id = fields.Many2one('appointment.meeting.room', string="Meeting Room", track_visibility='onchange')
    description = fields.Text(string='Remarks', track_visibility="onchange")
    appointment_date = fields.Date('Appointment Date', required=True, track_visibility="onchange")
    first_name = fields.Char(string="First Name", required=True, track_visibility='onchange')
    last_name = fields.Char(string="Last Name", required=True, track_visibility='onchange')
    gender_id = fields.Many2one('res.gender', string='Gender', required=True, track_visibility='onchange')
    phone = fields.Char(string="Phone", required=True, track_visibility='onchange')
    street = fields.Text(string="Street", required=True, track_visibility='onchange')
    street2 = fields.Text(string="Street", track_visibility='onchange')
    zipcode = fields.Char(string="Zip Code", required=True, track_visibility='onchange')
    city = fields.Char(string="City", required=True, track_visibility='onchange')
    country_id = fields.Many2one('res.country', string="Country", required=True, track_visibility='onchange')
    email = fields.Char(string="Email", required=True, track_visibility='onchange')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('approve', 'Approved'),
        ('done', 'Finished'),
        ('reject', 'Rejected')
    ], string='State', default='draft', readonly=True, copy=False, index=True, track_visibility='onchange')

    @api.depends('topic_id')
    def _compute_appointee(self):
        for rec in self:
            if rec.topic_id:
                rec.contact_id = rec.topic_id.contact_id

    @api.onchange('appointment_date', 'contact_id')
    def onchange_appointment_date(self):
        res = {}
        day = ''
        current_time =''
        today = datetime.today()
        self.timeslot_id = 0
        slots = []
        if self.appointment_date:
            appdate = datetime.strptime(self.appointment_date, "%Y-%m-%d")
            day = datetime.strftime(appdate, '%A')
            now = datetime.now()+timedelta(hours=6)
            current_time = now.strftime("%H:%M")

        appointment_slots = self.env['appointment.appointment'].search([('contact_id', '=', self.contact_id.id),
                                                                                  ('appointment_date', '=',
                                                                                   self.appointment_date),
                                                                                  ('state', 'in',
                                                                                   ['draft', 'confirm', 'approve'])])

        app_slots = [val.timeslot_id.id for val in appointment_slots]

        contact_slots = self.env['appointment.contact'].search([('id', '=', self.contact_id.id), ('state', '=', 'approve')])

        if self.appointment_date == datetime.strftime(today,"%Y-%m-%d"):
            for slot in contact_slots.timeslot_ids:
                slot_time_format ='{0:02.0f}:{1:02.0f}'.format(*divmod(slot.end_time * 60, 60))
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

    @api.one
    @api.constrains('meeting_room_id')
    def validate_meeting_room_id(self):
        if self.meeting_room_id:
            appointment = self.env['appointment.appointment'].search_count([('timeslot_id', '=', self.timeslot_id.id),
                                                                            ('meeting_room_id', '=', self.meeting_room_id.id),
                                                                      ('appointment_date', '=',
                                                                       self.appointment_date),
                                                                      ('state', 'in', ['draft',
                                                                                       'confirm', 'approve'])])
            if appointment > 1:
                raise ValidationError(_("This meeting room already booked.please select another room"))

    @api.one
    @api.constrains('email')
    def validate_mail(self):
        if self.email:
            if not Utility.valid_email(self.email):
                raise ValidationError('Email should be input a valid')

    @api.one
    @api.constrains('phone')
    def valid_mobile(self):
        if self.phone:
            if not Utility.valid_mobile(self.phone):
                raise ValidationError('Phone should be input a valid')

    @api.one
    @api.constrains('appointment_date', 'timeslot_id')
    def validate_appointment_day(self):
        if self.appointment_date:
            appdate = datetime.strptime(self.appointment_date, "%Y-%m-%d")
            day = datetime.strftime(appdate, '%A')
            if day.lower() != self.timeslot_id.day:
                raise ValidationError(_("Appointment day and time selection day should be "
                                        "same. Please change appointment date or time"))



    @api.multi
    def confirm_appointment(self):
        if self.state == 'draft':
            if not self.meeting_room_id:
                raise UserError(_('Unable to confirm an appointment without room. Please add room(s).'))

            result = self.env['ir.sequence'].next_by_code('appointment.sequence') or _('New')
            self.name = result
            self.state = 'confirm'

    @api.multi
    def reject_appointment(self):
        if self.state in ('confirm', 'draft', 'approve'):

            reject = {'template': 'appointments.mail_template_appointment_rej'}
            self.env['mail.mail'].mail_send(self.id, reject)

            rej_emk = {'template': 'appointments.mail_template_appointment_rej_emk'}
            self.env['mail.mail'].mail_send(self.id, rej_emk)

            self.state = 'reject'

    @api.multi
    def approve_appointment(self):
        if self.state == 'confirm':

            # app = {'template': 'appointments.mail_template_appointment_app'}
            # self.env['mail.mail'].mail_send(self.id, app)

            app_emk = {'template': 'appointments.mail_template_appointment_app_emk'}
            self.env['mail.mail'].mail_send(self.id, app_emk)

            self.state = 'approve'

    @api.multi
    def finish_appointment(self):
        if self.state == 'approve':
            # app = {'template': 'appointments.mail_template_appointment_app'}
            # self.env['mail.mail'].mail_send(self.id, app)

            app_emk = {'template': 'appointments.mail_template_appointment_app_emk'}
            self.env['mail.mail'].mail_send(self.id, app_emk)

            self.state = 'done'

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('You cannot delete this appointment'))
        return super(Appointment, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['draft', 'confirm', 'approve', 'done', 'reject'])]

    @api.model
    def post_appointments(self, vals, token=None):
        self.create(vals)
        return vals


