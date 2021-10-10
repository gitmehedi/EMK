# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventCategory(models.Model):
    _name = 'event.category'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'
    _description = "Event Category"

    name = fields.Char('Event Category', required=True, translate=True, track_visibility='onchange')
    event_category = fields.Integer(string="No of Events", compute='event_count_calculation')
    status = fields.Boolean(string='Status', default=True, track_visibility='onchange', )

    @api.multi
    def event_count_calculation(self):
        for records in self:
            events = self.env['event.event'].search([('event_type_id', '=', records.id)])
            records.event_count = len(events)

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise ValidationError(_('[DUPLICATE] Name already exist, choose another.'))

    @api.multi
    def unlink(self):
        for event in self:
            if event.event_count > 0:
                raise ValidationError(_('You cannot delete a record which has existing event!'))
        return super(EventCategory, self).unlink()
