# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_is_zero


class AssetDepreciationFlagWizard(models.TransientModel):
    _name = 'asset.depreciation.flag.wizard'

    flag = fields.Selection([('stop', 'Stop'), ('start', 'Start')], string='Depreciaton Flag', required=True)

    @api.multi
    def depreciation(self):
        for rec in self._context['active_ids']:
            asset = self.env['account.asset.asset'].browse(rec)
            flag = True if self.flag == 'stop' else False
            asset.write({'depreciation_flag': flag})

        return {'type': 'ir.actions.act_window_close'}
