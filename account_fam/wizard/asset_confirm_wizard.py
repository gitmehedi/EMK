# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning
from odoo.tools import float_compare, float_is_zero


class AssetConfirmWizard(models.TransientModel):
    _name = 'asset.confirm.wiazrd'

    @api.multi
    def confirm(self):
        for rec in self._context['active_ids']:
            asset = self.env['account.asset.asset'].browse(rec)
            if asset.state == 'draft' and not asset.depreciation_flag and not asset.allocation_status:
                asset.validate()
            else:
                flag = 'Active' if asset.depreciation_flag else 'In-Active'
                raise Warning(_('Asset {0} is in Status [{1}] with Awaiting Disposal [{2}]'.format(
                    asset.display_name,
                    asset.state, flag)))

        return {'type': 'ir.actions.act_window_close'}
