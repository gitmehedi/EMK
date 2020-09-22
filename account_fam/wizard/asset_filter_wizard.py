# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AssetFilterWizard(models.TransientModel):
    _name = 'asset.filter.wizard'

    operating_unit_id = fields.Many2one('operating.unit', string='Branch')
    category_id = fields.Many2one('account.asset.category', string='Asset Category',
                                  domain=[('parent_id', '!=', False)])

    @api.multi
    def search_branch(self):
        vals = []
        if self.operating_unit_id:
            vals.append(('current_branch_id', '=', self.operating_unit_id.id))
        assets = self.env['account.asset.asset'].search(vals)
        res_view = self.env.ref('account_fam.inherit_view_account_asset_asset_purchase_tree')
        domain = [('state', '=', 'open')]
        if self.operating_unit_id:
            domain.append(('current_branch_id', '=', self.operating_unit_id.id))
        if self.category_id:
            domain.append(('asset_type_id', '=', self.category_id.id))

        if not assets:
            raise ValidationError("No record found.")
        return {
            'name': _('Search Assets'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'account.asset.asset',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': domain,
        }
