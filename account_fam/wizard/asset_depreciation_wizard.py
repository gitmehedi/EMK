# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

from odoo import api, fields, models, _


class AssetDepreciationWizard(models.TransientModel):
    _name = 'asset.depreciation.wizard'

    date = fields.Date(string='Date', required=True, default=fields.Datetime.now)

    @api.multi
    def depreciate(self):

        if 'active_ids' in self._context:
            assets = self.env['account.asset.asset'].browse(self._context['active_ids'])
            for asset in assets:
                if asset.state == 'open' and not asset.depreciation_flag and asset.allocation_status:
                    self.depr_asset(asset)
        else:
            assets = self.env['account.asset.asset'].search(
                [('state', '=', 'open'), ('depreciation_flag', '=', False), ('allocation_status', '=', True)])
            for asset in assets:
                self.depr_asset(asset)

        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def depr_asset(self, asset):
        date = datetime.strptime(self.date, "%Y-%m-%d")
        asset.compute_depreciation_history(date, asset)
