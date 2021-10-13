# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventPoCType(models.Model):
    _name = 'event.poc.type'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Event POC Type'

    name = fields.Char('Name', required=True, translate=True, track_visibility='onchange')
    status = fields.Boolean(default=True, track_visibility='onchange')

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise ValidationError(_('[DUPLICATE] Name already exist, choose another.'))

    @api.multi
    def toggle_status(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.status = not record.status
