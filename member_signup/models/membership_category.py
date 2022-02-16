# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2 import IntegrityError
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.opa_utility.helper.utility import Utility,Message


class InheritedMembershipCategory(models.Model):
    _name = "membership.membership_category"
    _inherit = ['membership.membership_category', 'mail.thread', 'ir.needaction_mixin']
    _description = 'Membership Category'

    name = fields.Char(track_visibility='onchange')
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
                return super(InheritedMembershipCategory, rec).unlink()
            except IntegrityError:
                raise ValidationError(_(Message.UNLINK_INT_WARNING))

class InheritedProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'mail.thread', 'ir.needaction_mixin']

    list_price = fields.Float(track_visibility='onchange')
    membership_status = fields.Boolean(string='Default Membership', default=False, track_visibility='onchange')
    membership = fields.Boolean(help='Check if the product is eligible for membership.', track_visibility='onchange')
    membership_date_from = fields.Date(string='Membership Start Date',
                                       help='Date from which membership becomes active.', track_visibility='onchange')
    membership_date_to = fields.Date(string='Membership End Date',
                                     help='Date until which membership remains active.', track_visibility='onchange')
    membership_category_id = fields.Many2one(track_visibility='onchange')
    # active = fields.Boolean(track_visibility='onchange')
    membership_type = fields.Selection(selection=[('fixed', 'Fixed Dates'),
                                                  ('variable', 'Variable Periods')],
                                       string="Membership Type", track_visibility='onchange', required=True)
    property_account_income_id = fields.Many2one(track_visibility='onchange')

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise ValidationError(_(Message.UNIQUE_WARNING))

    @api.one
    def act_inactive(self):
        if self.state == 'approve':
            self.write({
                'active': False,
                'state': 'reject'
            })

    @api.one
    def act_active(self):
        if self.state == 'reject':
            self.write({
                'active': True,
                'state': 'approve'
            })


class MembershipWithdrawalReason(models.Model):
    _name = 'membership.withdrawal_reason'
    _inherit = ['membership.withdrawal_reason', 'mail.thread', 'ir.needaction_mixin']

    name = fields.Char(track_visibility='onchange')
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
                return super(MembershipWithdrawalReason, rec).unlink()
            except IntegrityError:
                raise ValidationError(_(Message.UNLINK_INT_WARNING))