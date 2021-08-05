# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class InheritedMembershipCategory(models.Model):
    _name = "membership.membership_category"
    _inherit = ['membership.membership_category', 'mail.thread', 'ir.needaction_mixin']
    _description = 'Membership Category'

    name = fields.Char(track_visibility='onchange')
    status = fields.Boolean(string='Status', default=True, track_visibility='onchange')

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise Exception(_('Name should not be duplicate.'))


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
    active = fields.Boolean(track_visibility='onchange')
    membership_type = fields.Selection(string="Membership Type", track_visibility='onchange')
    property_account_income_id = fields.Many2one(track_visibility='onchange')

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise Exception(_('Name should not be duplicate.'))


class MembershipWithdrawalReason(models.Model):
    _name = 'membership.withdrawal_reason'
    _inherit = ['membership.withdrawal_reason', 'mail.thread', 'ir.needaction_mixin']

    name = fields.Char(track_visibility='onchange')
    status = fields.Boolean(string='Status', default=True, track_visibility='onchange')

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise Exception(_('Name should not be duplicate.'))
