# -*- coding: utf-8 -*-
from psycopg2 import IntegrityError
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.opa_utility.helper.utility import Utility, Message


class EventTaskType(models.Model):
    _name = 'event.task.type'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Event Task Type'

    name = fields.Char('Task Name', required=True, translate=True, track_visibility='onchange')
    description = fields.Text('Description', required=True, translate=True, track_visibility='onchange')
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange')
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange', )

    @api.constrains('name')
    def _check_name(self):
        name = self.search(
            [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
             ('active', '=', False)])
        if len(name) > 1:
            raise ValidationError(_(Message.UNIQUE_WARNING))

    @api.multi
    def toggle_status(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.status = not record.status

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
                return super(EventTaskType, rec).unlink()
            except IntegrityError:
                raise ValidationError(_(Message.UNLINK_INT_WARNING))


class EventServiceType(models.Model):
    _name = 'event.service.type'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Event Service'

    name = fields.Char('Service Name', required=True, translate=True, track_visibility='onchange')
    service_type = fields.Selection([('internal', 'Internal'), ('external', 'External')], default='internal',
                                    required=True, translate=True, track_visibility='onchange')
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange')
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange', )

    @api.constrains('name')
    def _check_name(self):
        name = self.search(
            [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
             ('active', '=', False)])
        if len(name) > 1:
            raise ValidationError(_(Message.UNIQUE_WARNING))

    @api.multi
    def toggle_status(self):
        for record in self:
            record.status = not record.status

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
                return super(EventServiceType, rec).unlink()
            except IntegrityError:
                raise ValidationError(_(Message.UNLINK_INT_WARNING))
