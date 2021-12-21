import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError



class MeetingRoomConfigure(models.Model):
    _name = 'appointment.meeting.room'
    _description = "Meeting Room"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "id desc"

    name = fields.Char('Room Name', required=True, translate=True, track_visibility='onchange')
    max_seat = fields.Integer(string='Max Seat', required=True, track_visibility='onchange')
    min_seat = fields.Integer(string='Min Seat', required=True, track_visibility='onchange')
    status = fields.Boolean(default=True, track_visibility='onchange')

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise ValidationError(_('[DUPLICATE] Name already exist, choose another.'))

    @api.constrains('min_seat', 'max_seat')
    def _check_max_min(self):
        for rec in self:
            if rec.min_seat > rec.max_seat:
                raise ValidationError(_("Min Seat should not be greater than Max Seat."))

    def unlink(self):
        for rec in self:
            contact = self.env['appointment.appointment'].search([('meeting_room_id', '=', rec.id)])
            if contact:
                raise ValidationError(
                    _('[Warning] You cannot delete this meeting room. you may be trying to delete a record while other records still reference it'))

        return super(MeetingRoomConfigure, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        return [('status', '=', 'True')]