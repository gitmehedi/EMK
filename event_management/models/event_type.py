# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventManagementType(models.Model):
    _name = 'event.type'
    _inherit = ['event.type', 'mail.thread', 'ir.needaction_mixin']

    name = fields.Char('Event Type', required=True, translate=True, track_visibility='onchange')
    image = fields.Binary("Image", attachment=True, track_visibility='onchange',
                          help="This field holds the image used as image for the event, limited to 1080x720px.")
    event_count = fields.Integer(string="No of Events", compute='event_count_calculation')

    @api.multi
    def event_count_calculation(self):
        for records in self:
            events = self.env['event.event'].search([('event_type_id', '=', records.id)])
            records.event_count = len(events)

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise Exception(_('Name should not be duplicate.'))
