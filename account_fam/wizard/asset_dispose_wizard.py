# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AssetDisposeWizard(models.TransientModel):
    _name = 'asset.dispose.wizard'

    asset_ids = fields.Many2many('account.asset.asset','asset_dispose_rel','asset_id','dispose_id', required=True, string='Assets', domain="[('state','=','open')]")

    @api.multi
    def dispose(self):
        wizard_id = self.env.context.get('active_id', False)
        dispose_ins = self.env['account.asset.disposal.line']

        for asset in self.asset_ids:
            dispose_ins.create({
                'asset_id': asset.id,
                'asset_value': asset.value_residual,
                'depreciation_value': asset.value - asset.value_residual,
                'dispose_id': wizard_id,
                'journal_entry': 'unpost',
            })
        return {'type': 'ir.actions.act_window_close'}
