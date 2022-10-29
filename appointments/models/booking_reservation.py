import logging
from datetime import datetime

import dateutil.parser
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class Appointment(models.Model):
    _name = 'booking.reservation'
    _description = "Booking Reservation"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "id desc"

    @api.model
    def _get_required_date(self):
        return datetime.strftime(datetime.today(), DEFAULT_SERVER_DATETIME_FORMAT)

    name = fields.Char(string="Reference", readonly=True, copy=False, track_visibility='onchange')
    timeslot_id = fields.Many2one('booking.timeslot', string="Timeslot", required=True, track_visibility='onchange')
    booking_room_id = fields.Many2one('booking.room', string="Booking Room", required=True, track_visibility='onchange')
    description = fields.Text(string='Remarks', track_visibility="onchange")
    date = fields.Date('Booking Date', required=True, track_visibility="onchange")
    line_ids = fields.One2many('booking.reservation.line', 'line_id')

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

    @api.one
    @api.constrains('date')
    def validate_date(self):
        if self.date:
            app_date = datetime.strptime(self.date, '%Y-%m-%d')
            curr_date = dateutil.parser.parse(fields.Date.today())
            if app_date < curr_date:
                raise ValidationError(_("Appointment date cannot be past date from current date"))

    @api.one
    @api.constrains('booking_room_id')
    def validate_meeting_room_id(self):
        if self.booking_room_id:
            appointment = self.env['booking.reservation'].search_count([('timeslot_id', '=', self.timeslot_id.id),
                                                                        ('booking_room_id', '=',
                                                                         self.booking_room_id.id),
                                                                        ('date', '=', self.date),
                                                                        ('state', 'in',
                                                                         ['draft', 'confirm', 'approve'])])
            if appointment > 1:
                raise ValidationError(_("This room already booked.please select another room"))

    @api.multi
    def confirm_appointment(self):
        if self.state == 'draft':
            if not self.booking_room_id:
                raise UserError(_('Unable to confirm an appointment without room. Please add room(s).'))

            self.name = self.env['ir.sequence'].next_by_code('booking.sequence') or _('New')
            rooms = self.env['booking.room'].search([('id', '=', self.booking_room_id.id)], order='id desc')
            for room in rooms.line_ids:
                self.line_ids.create({
                    'line_id': self.id,
                    'seat_id': room.id,
                    'status': 'available'
                })

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

    class BookingReservationLine(models.Model):
        _name = 'booking.reservation.line'

        name = fields.Char(string="Name", track_visibility='onchange')
        phone = fields.Char(string="Phone", track_visibility='onchange')
        email = fields.Char(string="Email", track_visibility='onchange')
        membership_id = fields.Many2one('res.partner',string="Membership", track_visibility='onchange')
        line_id = fields.Many2one('booking.reservation', ondelete='cascade')
        seat_id = fields.Many2one('booking.room.line', string="Seat No")
        gender_id = fields.Many2one('res.gender', string='Gender', track_visibility='onchange')
        status = fields.Selection([('available', 'Available'), ('booked', 'Booked')], default='available')

        @api.multi
        def cancel_booking(self):
            if self.status == 'booked':
                self.status = 'available'
                self.name = ''
                self.phone = ''
                self.email = ''
