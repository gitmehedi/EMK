# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventManagementType(models.Model):
    _inherit = 'event.type'

    name = fields.Char(string="Name")
    image = fields.Binary("Image", attachment=True,
                          help="This field holds the image used as image for the event, limited to 1080x720px.")
    event_count = fields.Integer(string="# of Events", compute='event_count_calculation')

    @api.multi
    def event_count_calculation(self):
        for records in self:
            events = self.env['event.management'].search([('type_of_event', '=', records.id)])
            records.event_count = len(events)

