# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventManagementType(models.Model):
    _inherit = 'res.partner'

    is_organizer = fields.Boolean(default=False)
    event_count = fields.Integer("Events", compute='_compute_event_count',
                                 help="Number of events the partner has participated.")
    firstname = fields.Char("First Name", index=True, )
    middlename = fields.Char("Middle Name", index=True)
    lastname = fields.Char("Last Name", index=True)

    def _compute_event_count(self):
        for partner in self:
            partner.event_count = self.env['event.event'].search_count(
                [('organizer_id', '=', partner.id)])

    @api.multi
    def action_event_view(self):
        action = self.env.ref('event.action_event_view').read()[0]
        action['context'] = {}
        action['domain'] = [('organizer_id', '=', self.id)]
        return action
