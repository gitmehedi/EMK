# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ResGender(models.Model):
    _name = 'res.gender'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'
    _description = "Gender"

    name = fields.Char('Name', required=True, translate=True, track_visibility='onchange')
    status = fields.Boolean(string='Status', default=True, track_visibility='onchange')

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
        return super(ResGender, self).unlink()
