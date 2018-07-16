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
    _inherit = "product.template"

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
