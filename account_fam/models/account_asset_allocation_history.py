# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountAssetAllocationHistory(models.Model):
    _name = 'account.asset.allocation.history'
    _order = 'id desc'

    asset_id = fields.Many2one('account.asset.asset', ondelete='restrict')
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True)
    receive_date = fields.Datetime(string='Receive Date', required=True)
    transfer_date = fields.Datetime(string='Transfer Date')
    state = fields.Selection([('active', 'Active'), ('inactive', 'Active')], default='active', required=True)

    @api.multi
    def unlink(self):
        for rec in self:
            raise ValidationError(_('Allocation history shouldn\'t be deleted.'))


class AccountAsset(models.Model):
    _inherit = 'account.asset.asset'

    asset_allocation_ids = fields.One2many('account.asset.allocation.history', 'asset_id')
