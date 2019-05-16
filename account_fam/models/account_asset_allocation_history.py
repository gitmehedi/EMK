# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountAssetAllocationHistory(models.Model):
    _name = 'account.asset.allocation.history'
    _order = 'id desc'

    asset_user = fields.Char("Asset User")
    asset_id = fields.Many2one('account.asset.asset', ondelete='restrict')
    from_branch_id = fields.Many2one('operating.unit', string='From Branch')
    operating_unit_id = fields.Many2one('operating.unit', string='To Branch', required=True)
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sub Operating Unit')
    cost_centre_id = fields.Many2one('account.analytic.account', string='Cost Centre')
    receive_date = fields.Datetime(string='Receive Date', required=True)
    transfer_date = fields.Datetime(string='Transfer Date')
    state = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], default='active')
    move_id = fields.Many2one('account.move', string='Journal')

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit(self):
        if self.operating_unit_id:
            res = {}
            self.sub_operating_unit_id = 0
            branch = self.env['sub.openrating.unit'].search([('operating_unit_id', '=', self.operating_unit_id.id)])
            res['domain'] = {
                'sub_operating_unit_id': [('id', 'in', branch.ids)],
            }
            return res

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
