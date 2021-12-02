# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AssetDepreciationWizard(models.TransientModel):
    _name = 'asset.depreciation.wizard'

    def default_date(self):
        return self.env.user.company_id.batch_date

    date = fields.Date(string='Date', required=True, default=default_date)
    sure = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Double Check Execute Date?', required=True)

    @api.constrains('date')
    def check_date(self):
        if self.env.user.company_id.batch_date > self.date:
            raise ValidationError(_('Date should not be less than system date.'))

    @api.multi
    def depreciate(self):
        if self.sure == 'yes':
            lines = []
            if 'active_ids' in self._context:
                assets = self.env['account.asset.asset'].browse(self._context['active_ids'])
                for asset in assets:
                    if asset.state == 'open' and not asset.depreciation_flag and asset.allocation_status:
                        move = self.depr_asset(asset)
                        if move:
                            line = {
                                'journal_id': move.id,
                                'amount': move.amount,
                            }
                            lines.append((0, 0, line))
            else:
                move = self.env['account.asset.asset']._generate_depreciation(self.date)
                if move:
                    line = {
                        'journal_id': move.id,
                        'amount': move.amount,
                    }
                    lines.append((0, 0, line))

            if len(lines) > 0:
                self.env['account.asset.depreciation.history'].create({'date': self.date, 'line_ids': lines})

            return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def depr_asset(self, asset):
        date = datetime.strptime(self.date, "%Y-%m-%d")
        return asset.compute_depreciation_history(date, asset)
