import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

DAYS=[
    ('saturday','Saturday'),
    ('sunday','Sunday'),
    ('monday','Monday'),
    ('tuesday','Tuesday'),
    ('wednesday','wednesday'),
    ('thursday','Thursday'),
    ('friday','Friday'),
]


class AppointmentTimeSlot(models.Model):
    _name = 'appointment.timeslot'
    _description = "Appointment Time Slot"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "id desc"
    _rec_name="name"

    name = fields.Char(string="Name", readonly=True, track_visibility='onchange', compute='_compute_name')
    day = fields.Selection(DAYS, 'Day', required=True,  track_visibility="onchange")
    start_time = fields.Float(string="Start Time", required=True, digits=(2,2),  track_visibility="onchange")
    end_time = fields.Float(string="End Time", required=True, digits=(2,2), track_visibility="onchange")
    description = fields.Text(string="Description", track_visibility="onchange")
    contact_ids = fields.Many2many('appointment.contact', 'contact_timeslot_relation', 'contact_id', 'timeslot_id',
                                   string="Time Slot")
    status = fields.Boolean(string="Status", default=True, track_visibility='onchange')

    @api.multi
    def _compute_name(self):
        for rec in self:
            if rec.day and rec.start_time and rec.end_time:
                rec.name = '[%s - %s] %s' % (rec.start_time, rec.end_time, rec.day.title())

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise ValidationError(_('[DUPLICATE] Name already exist, choose another.'))

    @api.constrains('start_time', 'end_time')
    def _check_max_min(self):
        for rec in self:
            if rec.end_time >= rec.start_time:
                raise ValidationError(_("Start Time should not be greater than End Time."))

    @api.constrains('start_time', 'end_time')
    def _check_valid_time(self):
        for rec in self:
            if rec.start_time > 23:
                raise ValidationError(_("It should be valid date time"))
            if rec.end_time > 23:
                raise ValidationError(_("It should be valid date time"))

    @api.model
    def _needaction_domain_get(self):
        return [('status', '=', 'True')]
