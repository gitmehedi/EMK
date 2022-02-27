# -*- coding: utf-8 -*-
from psycopg2 import IntegrityError
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.opa_utility.helper.utility import Utility,Message



class EventRoom(models.Model):
    _name = 'event.room'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Event Room'

    name = fields.Char('Room Name', required=True, translate=True, track_visibility='onchange')
    max_seat = fields.Integer(string='Max Seat', required=True, track_visibility='onchange')
    min_seat = fields.Integer(string='Min Seat', required=True, track_visibility='onchange')
    service_ids = fields.Many2many('event.service.type', string='Services', required=True, track_visibility='onchange')
    event_count = fields.Integer(string="No of Events", compute='event_count_calculation')
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange')
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange', )

    @api.multi
    def event_count_calculation(self):
        for records in self:
            events = self.env['event.event'].search([('state', '=', 'done')])
            records.event_count = len(events)

    @api.constrains('min_seat', 'max_seat')
    def _check_max_min(self):
        for rec in self:
            if rec.min_seat > rec.max_seat:
                raise ValidationError(_("Min Seat should not be greater than Max Seat."))
            if rec.min_seat <= 0 or rec.max_seat <= 0:
                raise ValidationError(_("Min Seat and Max Seat should not be 0 ."))


    @api.constrains('name')
    def _check_name(self):
        name = self.search(
            [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
             ('active', '=', False)])
        if len(name) > 1:
            raise ValidationError(_(Message.UNIQUE_WARNING))

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('draft', 'approve', 'reject'))]

    @api.one
    def act_draft(self):
        if self.state == 'reject':
            self.write({
                'state': 'draft',
                'pending': True,
                'active': False,
            })

    @api.one
    def act_approve(self):
        if self.state == 'draft':
            self.write({
                'state': 'approve',
                'pending': False,
                'active': True,
            })

    @api.one
    def act_reject(self):
        if self.state == 'draft':
            self.write({
                'state': 'reject',
                'pending': False,
                'active': False,
            })

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'reject'):
                raise ValidationError(_(Message.UNLINK_WARNING))
            try:
                return super(EventRoom, rec).unlink()
            except IntegrityError:
                raise ValidationError(_(Message.UNLINK_INT_WARNING))