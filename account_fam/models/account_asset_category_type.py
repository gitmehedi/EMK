# -*- coding: utf-8 -*-

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import float_compare, float_is_zero


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    is_custom_depr = fields.Boolean(default=True, required=True)
    category_ids = fields.One2many('account.asset.category', 'parent_type_id', string="Category")
    parent_type_id = fields.Many2one('account.asset.category', string="Asset Type", ondelete="restrict")
    prorata = fields.Boolean(string='Prorata Temporis', default=True)
    depreciation_year = fields.Integer(string='Total Year', required=True, default=1)
    method_number = fields.Integer(string='Number of Depreciations',
                                   help="The number of depreciations needed to depreciate your asset")
    method = fields.Selection([('linear', 'Straight Line/Linear'), ('degressive', 'Reducing Method')],
                              string='Computation Method', required=True, default='linear',
                              help="Choose the method to use to compute the amount of depreciation lines.\n"
                                   "  * Linear: Calculated on basis of: Gross Value - Salvage Value/ Useful life of the fixed asset\n"
                                   "  * Reducing Method: Calculated on basis of: Residual Value * Depreciation Factor")
    asset_suspense_account_id = fields.Many2one('account.account', string='Asset Suspense Account', required=True,
                                                domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)])
    account_depreciation_id = fields.Many2one('account.account',
                                              string='Depreciation Entries: Asset Account (Accumulated)', )


    @api.onchange('parent_type_id')
    def onchange_asset_type(self):
        if self.parent_type_id:
            self.journal_id = self.parent_type_id.journal_id
            self.asset_suspense_account_id = self.parent_type_id.asset_suspense_account_id
            self.account_asset_id = self.parent_type_id.account_asset_id
            self.account_depreciation_id = self.parent_type_id.account_depreciation_id
            self.account_depreciation_expense_id = self.parent_type_id.account_depreciation_expense_id
            self.method = self.parent_type_id.method
            self.depreciation_year = self.parent_type_id.depreciation_year
            self.method_period = self.parent_type_id.method_period
            self.method_number = self.parent_type_id.method_number
            self.method_progress_factor = self.parent_type_id.method_progress_factor

    @api.onchange('depreciation_year')
    def onchange_depreciation_year(self):
        if self.depreciation_year:
            self.method_number = int(12 * self.depreciation_year)

    @api.constrains('depreciation_year')
    def check_depreciation_year(self):
        if self.depreciation_year < 1:
            raise ValidationError(_('Total year cannot be zero or negative value.'))

    @api.one
    def unlink(self):
        if self.category_ids:
            raise ValidationError(_("Please delete all asset category related with it."))
        return super(AccountAssetCategory, self).unlink()

    @api.constrains('name', 'parent_type_id')
    def _check_unique_name(self):
        if self.name:
            parent_type, msg = None, ''

            if self.parent_type_id:
                parent_type = self.parent_type_id.id
                msg = 'Asset Category already exists, Please choose another.'
            else:
                msg = 'Asset Type already exists, Please choose another.'

            name = self.search([('name', '=ilike', self.name), ('parent_type_id', '=', parent_type)])
            if len(name) > 1:
                raise ValidationError(_(msg))

