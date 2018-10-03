# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventTaskType(models.Model):
    _name = 'event.task.type'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char('Task Name', required=True, translate=True, track_visibility='onchange')
    status = fields.Boolean(default=True)

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise Exception(_('Name should not be duplicate.'))

    @api.multi
    def toggle_status(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.status = not record.status
