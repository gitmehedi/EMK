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

    method_progress_factor = fields.Float('Depreciation Factor', digits=(1, 3), default=0.0,
                                          track_visibility='onchange')
    category_ids = fields.One2many('account.asset.category', 'parent_id', string="Category")
    parent_id = fields.Many2one('account.asset.category', string="Asset Type Name", ondelete="restrict",
                                track_visibility='onchange')

    @api.onchange('parent_id')
    def onchange_asset_type(self):
        if self.parent_id:
            self.journal_id = self.parent_id.journal_id
            self.asset_suspense_account_id = self.parent_id.asset_suspense_account_id
            self.account_asset_id = self.parent_id.account_asset_id
            self.account_depreciation_id = self.parent_id.account_depreciation_id if self.parent_id.account_depreciation_id else None
            self.account_depreciation_expense_id = self.parent_id.account_depreciation_expense_id if self.parent_id.account_depreciation_expense_id else None
            self.account_asset_loss_id = self.parent_id.account_asset_loss_id
            self.account_asset_gain_id = self.parent_id.account_asset_gain_id
            self.asset_sale_suspense_account_id = self.parent_id.asset_sale_suspense_account_id
            self.method = self.parent_id.method
            self.depreciation_year = self.parent_id.depreciation_year
            self.method_period = self.parent_id.method_period
            self.method_number = self.parent_id.method_number
            self.method_progress_factor = self.parent_id.method_progress_factor
            self.code = self.parent_id.code


            self.asset_suspense_seq_id = self.parent_id.asset_suspense_seq_id
            self.account_asset_seq_id = self.parent_id.account_asset_seq_id
            self.account_asset_loss_seq_id = self.parent_id.account_asset_loss_seq_id
            self.account_asset_gain_seq_id = self.parent_id.account_asset_gain_seq_id
            self.asset_sale_suspense_seq_id = self.parent_id.asset_sale_suspense_seq_id
            self.account_depreciation_seq_id = self.parent_id.account_depreciation_seq_id if self.parent_id.account_depreciation_seq_id else None
            self.account_depreciation_expense_seq_id = self.parent_id.account_depreciation_expense_seq_id if self.parent_id.account_depreciation_expense_seq_id else None

    @api.model
    def create(self, vals):
        if 'parent_id' in vals:
            if vals.get('code', 'New') == 'New':
                seq = self.env['ir.sequence']
                vals['code'] = seq.next_by_code('account.asset.category') or ''
        return super(AccountAssetCategory, self).create(vals)

    @api.one
    def unlink(self):
        if self.category_ids:
            raise ValidationError(_("Please delete all asset category related with it."))
        return super(AccountAssetCategory, self).unlink()

    @api.constrains('name', 'parent_id')
    def _check_unique_name(self):
        if self.name:
            parent_type, msg = None, ''

            if self.parent_id:
                parent_type = self.parent_id.id
                msg = 'Asset Category already exists, Please choose another.'
            else:
                msg = 'Asset Type already exists, Please choose another.'

            name = self.search([('name', '=ilike', self.name), ('parent_id', '=', parent_type)])
            if len(name) > 1:
                raise ValidationError(_(msg))

    @api.one
    def unlink(self):
        from psycopg2 import IntegrityError
        if self.category_ids:
            raise ValidationError(_("Please delete all asset category related with it."))
        try:
            return super(AccountAssetCategory, self).unlink()
        except IntegrityError:
            raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                    "- deletion: you may be trying to delete a record while other records still reference it"))
