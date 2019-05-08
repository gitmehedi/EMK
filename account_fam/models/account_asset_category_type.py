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
    # category_ids = fields.One2many('account.asset.category', 'parent_id', string="Category")
    # parent_id = fields.Many2one('account.asset.category', string="Asset Type", ondelete="restrict")
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
                                                domain=[('deprecated', '=', False)])
    account_depreciation_id = fields.Many2one('account.account', required=True,
                                              domain=[('deprecated', '=', False)],
                                              string='Accumulated Depreciation A/C', )
    account_depreciation_expense_id = fields.Many2one('account.account', string='Depreciation Exp. A/C',
                                                      required=True, domain=[('internal_type', '=', 'other'),
                                                                             ('deprecated', '=', False)],
                                                      oldname='account_income_recognition_id',
                                                      help="Account used in the periodical entries, to record a part of the asset as expense.")
    account_asset_loss_id = fields.Many2one('account.account', required=True,
                                            domain=[('deprecated', '=', False)],
                                            string='Asset Loss A/C')
    account_asset_gain_id = fields.Many2one('account.account', required=True,
                                            domain=[('deprecated', '=', False)],
                                            string='Asset Gain A/C')
    asset_sale_suspense_account_id = fields.Many2one('account.account', required=True,
                                                     domain=[('deprecated', '=', False)],
                                                     string='Asset Sales Suspense Account', )

    @api.onchange('depreciation_year')
    def onchange_depreciation_year(self):
        if self.depreciation_year:
            self.method_number = int(12 * self.depreciation_year)

    @api.constrains('depreciation_year')
    def check_depreciation_year(self):
        if self.depreciation_year < 1:
            raise ValidationError(_('Total year cannot be zero or negative value.'))

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search([['name', '=ilike', self.name]])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.one
    def name_get(self):
        name = self.name
        if self.name:
            name = '%s' % (self.name)
        return (self.id, name)

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()
