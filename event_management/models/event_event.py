# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventEvent(models.Model):
    _inherit = 'event.event'

    event_type_id = fields.Many2one(
        'event.type', string='Category',
        readonly=False, states={'done': [('readonly', True)]},
        oldname='type', required=True)
