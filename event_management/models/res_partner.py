# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventManagementType(models.Model):
    _inherit = 'res.partner'


    is_organizer = fields.Boolean(default=False)

