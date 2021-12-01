# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    asset_type_id = fields.Many2one('account.asset.category', string='Asset Category', company_dependent=True,
                                    ondelete="restrict")
    type = fields.Selection(selection_add=[('asset', 'Assets')])

    @api.onchange('asset_category_id')
    def onchange_asset_category(self):
        if self.asset_category_id:
            self.asset_type_id = None
            category_ids = self.env['account.asset.category'].search(
                [('parent_id', '=', self.asset_category_id.id)])
            return {
                'domain': {'asset_type_id': [('id', 'in', category_ids.ids)]}
            }


class ProductTemplate(models.Model):
    _inherit = 'product.product'

    @api.onchange('type')
    def onchange_type(self):
        if self.type != 'asset':
            self.asset_category_id = 0
            self.asset_type_id = 0
