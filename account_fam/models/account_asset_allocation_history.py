# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountAssetAllocationHistory(models.Model):
    _name = 'account.asset.allocation.history'
    _order = 'id desc'

    asset_user = fields.Char("Asset User", track_visibility='onchange')
    asset_id = fields.Many2one('account.asset.asset', ondelete='restrict', track_visibility='onchange')
    from_branch_id = fields.Many2one('operating.unit', string='From Branch', track_visibility='onchange')
    operating_unit_id = fields.Many2one('operating.unit', string='To Branch', required=True,
                                        track_visibility='onchange')
    cost_centre_id = fields.Many2one('account.analytic.account', string='Cost Centre', required=True, track_visibility='onchange')
    receive_date = fields.Date(string='Receive Date', required=True, track_visibility='onchange')
    transfer_date = fields.Date(string='Transfer Date', track_visibility='onchange')
    state = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], default='active',
                             track_visibility='onchange')
    move_id = fields.Many2one('account.move', string='Journal')

    @api.onchange("asset_user")
    def onchange_strips(self):
        if self.asset_user:
            self.asset_user = self.asset_user.strip()

    @api.multi
    def unlink(self):
        for rec in self:
            raise ValidationError(_('Allocation history shouldn\'t be deleted.'))


class AccountAsset(models.Model):
    _inherit = 'account.asset.asset'

    asset_allocation_ids = fields.One2many('account.asset.allocation.history', 'asset_id')
