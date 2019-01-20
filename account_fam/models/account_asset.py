# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    category_ids = fields.One2many('account.asset.category', 'parent_type_id', string="Category")
    parent_type_id = fields.Many2one('account.asset.category', string="Asset Type", ondelete="restrict")

    @api.one
    def unlink(self):
        if self.category_ids:
            raise ValidationError(_("Please delete all asset category related with it."))
        return super(AccountAssetCategory, self).unlink()

    @api.constrains('name', 'parent_type_id')
    def _check_unique_name(self):
        if self.name:
            parent_type, msg = None, ''

            if self.parent_type_id:
                parent_type = self.parent_type_id.id
                msg = 'Asset Category already exists, Please choose another.'
            else:
                msg = 'Asset Type already exists, Please choose another.'

            name = self.search([('name', '=ilike', self.name), ('parent_type_id', '=', parent_type)])
            if len(name) > 1:
                raise ValidationError(_(msg))


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'
    _order = 'id desc'

    receive_date = fields.Date(string='Receive Date')
    asset_usage_date = fields.Date(string='Allocation Date', help='Asset Allocation/Usage Date')
    asset_type_id = fields.Many2one('account.asset.category', string='Asset Type', required=True, change_default=True,
                                    readonly=True, states={'draft': [('readonly', False)]})
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=True)
    invoice_date = fields.Date(related='invoice_id.date', string='Invoice Date')

    @api.onchange('category_id')
    def onchange_asset_category(self):
        if self.category_id:
            self.asset_type_id = None
            category_ids = self.env['account.asset.category'].search(
                [('parent_type_id', '=', self.category_id.id)])
            return {
                'domain': {'asset_type_id': [('id', 'in', category_ids.ids)]}
            }
