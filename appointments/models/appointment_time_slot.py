import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AppointmentTimeSlot(models.Model):
    _name = 'appointment.timeslot'
    _description = "Appointment Time Slot"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "id desc"

    @api.depends('end_time')
    def _compute_name(self):
        for rec in self:
            if rec.end_time:
                if self.day == 'saturday':
                    day = 'Sat'
                elif self.day == 'sunday':
                    day = 'Sun'
                elif self.day == 'monday':
                    day = 'Mon'
                elif self.day == 'tuesday':
                    day = 'Tue'
                elif self.day == 'wednesday':
                    day = 'Wed'
                elif self.day == 'thursday':
                    day = 'Thu'
                elif self.day == 'friday':
                    day = 'Fri'
                self.name = day + ' (' + str(self.start_time) + '-' + str(self.end_time)+')'

    # @api.model
    # def create(self, vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code('appointment.timeslot.sequence') or _('New')
    #     result = super(AppointmentTimeSlot, self).create(vals)
    #     return result

    name = fields.Char(string="Name", required=True, readonly=True, translate=True, compute='_compute_name', track_visibility='onchange' )
    day = fields.Selection([('saturday', 'Saturday'), ('sunday', 'Sunday'),('monday', 'Monday'),
                            ('tuesday', 'Tuesday'),('wednesday', 'Wednesday'), ('thursday', 'Thursday'),
                            ('friday', 'Friday')], 'Day',
                     default="saturday", required=True,  track_visibility="onchange")
    start_time = fields.Float(string="Start Time", required=True,  track_visibility="onchange" )
    end_time = fields.Float(string="End Time", required=True, track_visibility="onchange")
    description = fields.Text(string="Description", track_visibility="onchange")
    status = fields.Boolean(string="Status", default=True, track_visibility='onchange')

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise ValidationError(_('[DUPLICATE] Name already exist, choose another.'))

    @api.model
    def _needaction_domain_get(self):
        return [('status', '=', 'True')]
