# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class InheritedMembershipCategory(models.Model):
    _inherit = "membership.membership_category"

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
    membership = fields.Boolean(help='Check if the product is eligible for membership.',track_visibility='onchange')
    membership_date_from = fields.Date(string='Membership Start Date',
                                       help='Date from which membership becomes active.',track_visibility='onchange')
    membership_date_to = fields.Date(string='Membership End Date',
                                     help='Date until which membership remains active.',track_visibility='onchange')

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise Exception(_('Name should not be duplicate.'))


class InheritedMembershipWithdrawalReason(models.Model):
    _inherit = "membership.withdrawal_reason"

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise Exception(_('Name should not be duplicate.'))
