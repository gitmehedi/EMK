# -*- coding: utf-8 -*-

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import float_compare, float_is_zero


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    asset_type_id = fields.Many2one('account.asset.category', string='Asset Category', required=True, change_default=True,
                                    readonly=True, states={'draft': [('readonly', False)]})


    @api.onchange('category_id')
    def onchange_asset_category(self):
        if self.category_id:
            self.asset_type_id = None
            category_ids = self.env['account.asset.category'].search(
                [('parent_id', '=', self.category_id.id)])
            return {
                'domain': {'asset_type_id': [('id', 'in', category_ids.ids)]}
            }

