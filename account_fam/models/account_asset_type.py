# -*- coding: utf-8 -*-

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import float_compare, float_is_zero


class AccountAssetCategory(models.Model):
    _name = 'account.asset.category'
    _inherit = ['account.asset.category', 'mail.thread']
    _order = 'code ASC'

    code = fields.Char(string='Code', size=4)
    active = fields.Boolean(default=True, track_visibility='onchange')
    name = fields.Char(required=True, index=True, string="Asset Type", size=50, track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, track_visibility='onchange')
    method_period = fields.Integer(string='One Entry Every', default=1, track_visibility='onchange',
                                   help="State here the time between 2 depreciations, in months", required=True)
    is_custom_depr = fields.Boolean(default=True, required=True)
    prorata = fields.Boolean(string='Prorata Temporis', default=True)
    depreciation_year = fields.Integer(string='Asset Life (In Year)', required=True, default=1,
                                       track_visibility='onchange')
    method_number = fields.Integer(string='Number of Depreciations',
                                   help="The number of depreciations needed to depreciate your asset")
    method = fields.Selection([('linear', 'Straight Line/Linear'), ('degressive', 'Reducing Method')],
                              string='Computation Method', required=True, default='linear', track_visibility='onchange',
                              help="Choose the method to use to compute the amount of depreciation lines.\n"
                                   "  * Linear: Calculated on basis of: Gross Value - Salvage Value/ Useful life of the fixed asset\n"
                                   "  * Reducing Method: Calculated on basis of: Residual Value * Depreciation Factor")
    account_asset_id = fields.Many2one('account.account', string='Asset Account', required=True,
                                       track_visibility='onchange',
                                       domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)],
                                       help="Account used to record the purchase of the asset at its original price.")
    asset_suspense_account_id = fields.Many2one('account.account', string='Asset Suspense Account', required=True,
                                                domain=[('deprecated', '=', False)], track_visibility='onchange')
    account_depreciation_id = fields.Many2one('account.account', required=True, track_visibility='onchange',
                                              domain=[('deprecated', '=', False)],
                                              string='Accumulated Depreciation A/C', )
    account_depreciation_expense_id = fields.Many2one('account.account', string='Depreciation Exp. A/C',
                                                      track_visibility='onchange',
                                                      required=True, domain=[('internal_type', '=', 'other'),
                                                                             ('deprecated', '=', False)],
                                                      oldname='account_income_recognition_id',
                                                      help="Account used in the periodical entries, to record a part of the asset as expense.")
    account_asset_loss_id = fields.Many2one('account.account', required=True, track_visibility='onchange',
                                            domain=[('deprecated', '=', False)],
                                            string='Asset Loss A/C')
    account_asset_gain_id = fields.Many2one('account.account', required=True, track_visibility='onchange',
                                            domain=[('deprecated', '=', False)],
                                            string='Asset Gain A/C')
    asset_sale_suspense_account_id = fields.Many2one('account.account', required=True, track_visibility='onchange',
                                                     domain=[('deprecated', '=', False)],
                                                     string='Asset Sales Suspense Account', )

    @api.model
    def create(self, vals):
        if 'parent_id' not in vals:
            if vals.get('code', 'New') == 'New':
                seq = self.env['ir.sequence']
                vals['code'] = seq.next_by_code('account.asset.type') or ''
        return super(AccountAssetCategory, self).create(vals)

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
            name = self.search(
                [('name', '=ilike', self.name.strip()), '|', ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.one
    def name_get(self):
        if self.parent_id:
            name = '%s' % (self.name)
        else:
            name = '[%s] %s' % (self.code, self.name)
        return (self.id, name)

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()
