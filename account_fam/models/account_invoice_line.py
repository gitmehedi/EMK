# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    asset_category_id = fields.Many2one('account.asset.category', string='Asset Type', ondelete="restrict")
    asset_type_id = fields.Many2one('account.asset.category', string='Asset Category', ondelete="restrict")

    @api.onchange('asset_category_id')
    def onchange_asset_category(self):
        if self.asset_category_id:
            self.asset_type_id = None
            category_ids = self.env['account.asset.category'].search(
                [('parent_type_id', '=', self.asset_category_id.id)])
            return {
                'domain': {'asset_type_id': [('id', 'in', category_ids.ids)]}
            }
