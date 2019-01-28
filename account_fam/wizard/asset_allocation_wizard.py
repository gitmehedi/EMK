# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AssetAllocationWizard(models.TransientModel):
    _name = 'asset.allocation.wizard'

    date = fields.Date(default=fields.Date.today(), string='Allocation/Relocation Date')
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True)
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sub Branch')

    @api.onchange('operating_unit_id')
    def onchange_operating_unit(self):
        if self.operating_unit_id:
            self.sub_operating_unit_id = None
            sub_operating = self.env['sub.operating.unit'].search(
                [('operating_unit_id', '=', self.operating_unit_id.id)])
            return {
                'domain': {'sub_operating_unit_id': [('id', 'in', sub_operating.ids)]}
            }

    @api.multi
    def allocation(self):
        asset_id = self.env.context.get('active_id', False)
        asset = self.env['account.asset.asset'].browse(asset_id)

        last_allocation = self.env['account.asset.allocation.history'].search(
            [('asset_id', '=', asset_id), ('status', '=', True), ('transfer_date', '=', False)])

        if last_allocation:
            if last_allocation.receive_date >= self.date:
                raise ValidationError(_("Receive date shouldn\'t less than previous receive date."))

            last_allocation.write({
                'transfer_date': datetime.strptime(self.date, '%Y-%m-%d') + timedelta(days=-1),
                'status': False,
            })

        self.env['account.asset.allocation.history'].create({
            'asset_id': asset_id,
            'operating_unit_id': self.operating_unit_id.id,
            'receive_date': self.date,
            'status': True,
        })

        # asset.write(asset_vals)
        # asset.compute_depreciation_board()
        # tracked_fields = self.env['account.asset.asset'].fields_get(['method_number', 'method_period', 'method_end'])
        # changes, tracking_value_ids = asset._message_track(tracked_fields, old_values)
        # if changes:
        #     asset.message_post(subject=_('Depreciation board modified'), body=self.name,
        #                        tracking_value_ids=tracking_value_ids)
        return {'type': 'ir.actions.act_window_close'}
