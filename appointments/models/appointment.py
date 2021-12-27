import logging
from datetime import datetime
import dateutil.parser
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.appointments.helpers import functions

_logger = logging.getLogger(__name__)


class Appointment(models.Model):
    _name = 'appointment.appointment'
    _description = "Appointment"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "id desc"

    @api.model
    def _get_required_date(self):
        return datetime.strftime(datetime.today(), DEFAULT_SERVER_DATETIME_FORMAT)

    name = fields.Char(string="Name", readonly=True, copy=False, track_visibility='onchange')
    # client_id = fields.Many2one('res.partner',string="Client")
    topic_id = fields.Many2one('appointment.topics', string="Topics", required=True, track_visibility='onchange')
    contact_id = fields.Many2one('appointment.contact', string="Appointee", required=True, track_visibility='onchange')
    timeslot_id = fields.Many2one('appointment.timeslot', string="Time", required=True, track_visibility='onchange')
    type_id = fields.Many2one('appointment.type', string="Appointment Type", required=True, track_visibility='onchange')
    meeting_room_id = fields.Many2many('appointment.meeting.room', 'appointment_meeting_room_rel', 'appointment_id',
                                       'meeting_room_id', string='Room Allocation', track_visibility='onchange')

    description = fields.Text(string='Remarks', track_visibility="onchange")
    appointment_date = fields.Date('Appointment Date', required=True, track_visibility="onchange")
    first_name = fields.Char(string="First Name", required=True, track_visibility='onchange')
    last_name = fields.Char(string="Last Name", required=True, track_visibility='onchange')
    gender = fields.Many2one('res.gender', string='Gender', required=True, track_visibility='onchange')
    date_of_birth = fields.Date(string="Date of Birth", required=True, track_visibility='onchange')
    phone = fields.Char(string="Phone", required=True, track_visibility='onchange')
    address = fields.Text(string="Address", required=True, track_visibility='onchange')
    city = fields.Char(string="City", required=True, track_visibility='onchange')
    country = fields.Many2one('res.country', string="Country", required=True, track_visibility='onchange')
    email = fields.Char(string="Email", required=True, track_visibility='onchange')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Approved'),
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
        if self.appointment_date:
            appdate = datetime.strptime(self.appointment_date, "%Y-%m-%d")
            day = datetime.strftime(appdate, '%A')
            timeslot_ids = self.env['appointment.timeslot'].search(
                [('day', '=', day.lower()), ('id', 'in', self.contact_id.timeslot_ids.ids)])
            if timeslot_ids:
                res['domain'] = {
                    'timeslot_id': [('id', 'in', timeslot_ids.ids)]
                }
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

    @api.one
    @api.constrains('appointment_date')
    def validate_appointment_date(self):
        if self.appointment_date:
            app_date = datetime.strptime(self.appointment_date, '%Y-%m-%d')
            curr_date = dateutil.parser.parse(fields.Date.today())
            if app_date < curr_date:
                raise ValidationError(_("Appointment date cannot be past date from current date"))

    @api.one
    @api.constrains('date_of_birth')
    def validate_birth_date(self):
        if self.date_of_birth:
            birth_date = datetime.strptime(self.date_of_birth, '%Y-%m-%d')
            curr_date = dateutil.parser.parse(fields.Date.today())
            if birth_date >= curr_date:
                raise ValidationError(_("Birth date cannot be future date and current date"))

    @api.one
    @api.constrains('email')
    def validate_mail(self):
        if self.email:
            if not functions.valid_email(self.email):
                raise ValidationError('Email should be input a valid')

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
        if self.state == 'confirm':
            # reject = {}
            # reject['template'] = 'appointments.mail_template_appointment_rej'
            # self.env['mail.mail'].mail_send(self.id, reject)
            #
            # rej_emk = {}
            # rej_emk['template'] = 'appointments.mail_template_appointment_rej_emk'
            # self.env['mail.mail'].mail_send(self.id, rej_emk)
            self.state = 'reject'

    @api.multi
    def approve_appointment(self):
        if self.state == 'confirm':
            # app = {}
            # app['template'] = 'appointments.mail_template_appointment_app'
            # self.env['mail.mail'].mail_send(self.id, app)
            #
            # app_emk = {}
            # app_emk['template'] = 'appointments.mail_template_appointment_app_emk'
            # self.env['mail.mail'].mail_send(self.id, app_emk)

            self.state = 'done'


    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('You cannot delete this appointment'))
        return super(Appointment, self).unlink()


    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['draft', 'confirm', 'done', 'reject'])]
