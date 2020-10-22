# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AssetDisposeWizard(models.TransientModel):
    _name = 'asset.dispose.wizard'

    def default_branch(self):
        active_id = self.env.context['active_id']
        asset_sale = self.env['account.asset.disposal'].browse(active_id)
        return asset_sale.branch_id

    branch_id = fields.Many2one('operating.unit', default=default_branch)
    asset_ids = fields.Many2many('account.asset.asset', string='Assets')

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
