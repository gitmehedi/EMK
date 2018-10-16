# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventEvent(models.Model):
    _inherit = 'event.event'

    organizer_id = fields.Many2one('res.partner', string='Organizer Name', domain=[('organizer', '=', True)],
                                   default=False, required=True)

    total_seat_available = fields.Integer(string="Total Seat Available", compute='compute_total_seat')

    event_book_ids = fields.One2many('event.room.book', 'event_id', string='Event Rooms')
    event_task_ids = fields.One2many('event.task.list', 'event_id', string='Event Tasks')

    @api.depends('event_book_ids')
    def compute_total_seat(self):
        for record in self:
            record.total_seat_available = sum([rec.seat_no for rec in record.event_book_ids])


    @api.multi
    @api.constrains('date_begin')
    def _check_date_begin(self):
        dt = fields.Date.today()
        if self.date_begin < dt:
            raise ValidationError(_("Event Start Date cannot be past day from current date"))


class EventRegistration(models.Model):
    _inherit = 'event.registration'
    _order='id desc'

    temp_seq_name = fields.Char(string='Sequence Name')
    date_of_birth = fields.Date(string='Date of Birth', required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], required=True,
                              default='male', string='Gender')
    profession = fields.Char(string='Profession', required=True, default=False)


    @api.model
    def create(self, vals):
        registration = super(EventRegistration, self).create(vals)
        if registration:
            sequence = self.env['ir.sequence'].next_by_code('event.attendee') or 'New'
            registration.write({'temp_seq_name': sequence})
        return registration

