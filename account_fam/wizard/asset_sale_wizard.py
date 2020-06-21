# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AssetSaleWizard(models.TransientModel):
    _name = 'asset.sale.wizard'

    asset_ids = fields.Many2many('account.asset.asset','asset_sale_rel','asset_id','dispose_id', required=True, string='Assets', domain="[('state','=','open')]")

    @api.multi
    def sale(self):
        wizard_id = self.env.context.get('active_id', False)
        sale_ins = self.env['account.asset.sale.line']

        for asset in self.asset_ids:
            sale_ins.create({
                'asset_id': asset.id,
                'asset_value': asset.value_residual,
                'depreciation_value': asset.value - asset.value_residual,
                'sale_value': asset.value_residual,
                'sale_id': wizard_id,
                'journal_entry': 'unpost',
            })
        return {'type': 'ir.actions.act_window_close'}
