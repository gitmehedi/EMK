# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_is_zero


class AssetDepreciationFlagWizard(models.TransientModel):
    _name = 'asset.depreciation.flag.wizard'

    flag = fields.Selection([('stop', 'Stop'), ('start', 'Start')], string='Awaiting Disposal', required=True)

    @api.multi
    def depreciation(self):
        for rec in self._context['active_ids']:
            asset = self.env['account.asset.asset'].browse(rec)
            if asset.state == 'open' and asset.allocation_status == True and asset.asset_status == 'active':
                flag = True if self.flag == 'stop' else False
                asset.write({'depreciation_flag': flag, 'awaiting_dispose_date': fields.Datetime.now()})
            else:
                name = asset.asset_seq if asset.asset_seq else asset.name
                raise ValidationError(_('Asset [{0}] should in Running status.'.format(name)))

        return {'type': 'ir.actions.act_window_close'}
