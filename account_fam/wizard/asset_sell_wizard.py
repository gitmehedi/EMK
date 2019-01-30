# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AssetSellWizard(models.TransientModel):
    _name = 'asset.sell.wizard'

    asset_ids = fields.Many2many('account.asset.asset', required=True, string='Assets', domain="[('state','=','open')]")

    @api.multi
    def sell(self):
        wizard_id = self.env.context.get('active_id', False)
        sell_ins = self.env['account.asset.sell.line']

        for asset in self.asset_ids:
            sell_ins.create({
                'asset_id': asset.id,
                'asset_value': asset.value_residual,
                'depreciation_value': asset.value - asset.value_residual,
                'sell_value': asset.value_residual,
                'sell_id': wizard_id,
                'journal_entry': 'unpost',
            })
        return {'type': 'ir.actions.act_window_close'}
