# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from lxml import etree

from odoo import api, fields, models, _
from odoo.osv.orm import setup_modifiers
from odoo.exceptions import Warning


class AssetModify(models.TransientModel):
    _inherit = 'asset.modify'

    method_number = fields.Integer(string='One Entry (In Month)', required=True, default=1, invisible=True)
    method_progress_factor = fields.Float('Degressive Factor')
    depreciation_year = fields.Integer(string='Asset Life (In Year)', required=True)
    method = fields.Selection([('linear', 'Straight Line/ Linear'), ('degressive', 'Reducing Method')],
                              string='Computation Method', required=True, default='linear',
                              help="Choose the method to use to compute the amount of depreciation lines.\n"
                                   "  * Linear: Calculated on basis of: Gross Value - Salvage Value/ Useful life of the fixed asset\n"
                                   "  * Reducing Method: Calculated on basis of: Residual Value * Depreciation Factor")

    @api.onchange('depreciation_year')
    def onchange_depreciation_year(self):
        if self.depreciation_year:
            self.method_number = int(12 * self.depreciation_year)

    @api.model
    def default_get(self, fields):
        res = super(AssetModify, self).default_get(fields)
        asset_id = self.env.context.get('active_id')
        asset = self.env['account.asset.asset'].browse(asset_id)

        if 'name' in fields:
            res.update({'name': asset.name})
        if 'method_number' in fields and asset.method_time == 'number':
            res.update({'method_number': asset.method_number})
        if 'method_period' in fields:
            res.update({'method_period': asset.method_period})
        if 'method_end' in fields and asset.method_time == 'end':
            res.update({'method_end': asset.method_end})
        if 'method' in fields:
            res.update({'method': asset.method})
        if 'method_progress_factor' in fields:
            res.update({'method_progress_factor': asset.method_progress_factor})
        if 'depreciation_year' in fields:
            res.update({'depreciation_year': asset.depreciation_year})
        if self.env.context.get('active_id'):
            active_asset = self.env['account.asset.asset'].browse(self.env.context.get('active_id'))
            res['asset_method_time'] = active_asset.method_time
        return res

    @api.multi
    def modify(self):
        """ Modifies the duration of asset for calculating depreciation
        and maintains the history of old values, in the chatter.
        """
        for rec in self._context['active_ids']:
            asset = self.env['account.asset.asset'].browse(rec)
            if asset.state == 'open' and not asset.depreciation_flag:
                old_values = {
                    'method_number': asset.method_number,
                    'method_period': asset.method_period,
                    'method_end': asset.method_end,
                    'method_progress_factor': asset.method_progress_factor,
                    'depreciation_year': asset.depreciation_year,
                    'method': asset.method,
                }
                asset_vals = {
                    'method_number': self.method_number,
                    'method_period': self.method_period,
                    'method_end': self.method_end,
                    'method_progress_factor': self.method_progress_factor,
                    'depreciation_year': self.depreciation_year,
                    'method': self.method,
                }
                asset.write(asset_vals)

                tracked_fields = self.env['account.asset.asset'].fields_get(
                    ['method_number', 'method_period', 'method_end'])
                changes, tracking_value_ids = asset._message_track(tracked_fields, old_values)
                if changes:
                    asset.message_post(subject=_('Depreciation board modified'), body=self.name,
                                       tracking_value_ids=tracking_value_ids)
            else:
                flag = 'Active' if asset.depreciation_flag else 'In-Active'
                raise Warning(_('Depreciation of Asset {0} is in Status [{1}] with Depreciation Flag [{2}]'.format(asset.display_name,
                                                                                                     asset.state,flag)))

        return {'type': 'ir.actions.act_window_close'}
