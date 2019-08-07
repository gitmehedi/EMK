# -*- coding: utf-8 -*-

import random

from odoo import api, fields, models, _


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    asset_category_id = fields.Many2one('account.asset.category', string='Asset Type', ondelete="restrict")
    asset_type_id = fields.Many2one('account.asset.category', string='Asset Category', ondelete="restrict")

    @api.onchange('asset_category_id')
    def onchange_asset_category_id(self):
        if self.invoice_id.type == 'out_invoice' and self.asset_category_id:
            self.account_id = self.asset_category_id.account_asset_id.id
        elif self.invoice_id.type == 'in_invoice' and self.asset_category_id:
            self.account_id = self.asset_category_id.account_asset_id.id

    @api.one
    def asset_create(self):
        if self.asset_category_id:
            asset_value = self.price_subtotal / self.quantity
            batch_seq = {val: key for key, val in enumerate(self.invoice_id.invoice_line_ids.ids)}
            for rec in range(0, int(self.quantity)):
                vals = {
                    'name': self.name,
                    'code': self.invoice_id.number or False,
                    'category_id': self.asset_category_id.id,
                    'asset_type_id': self.asset_type_id.id,
                    'value': asset_value,
                    'partner_id': self.invoice_id.partner_id.id,
                    'company_id': self.invoice_id.company_id.id,
                    'currency_id': self.invoice_id.company_currency_id.id,
                    'date': self.invoice_id.date_invoice,
                    'invoice_id': self.invoice_id.id,
                    'operating_unit_id': self.invoice_id.operating_unit_id.id,
                    'current_branch_id': self.invoice_id.operating_unit_id.id,
                    'prorata': True,
                    'batch_no': "{0}-{1}".format(self.invoice_id.number, batch_seq[self.id]),
                    'cost_centre_id': self.invoice_id.account_analytic_id.id if self.invoice_id.account_analytic_id else None,
                }

                changed_vals = self.env['account.asset.asset'].onchange_category_id_values(vals['category_id'])
                vals.update(changed_vals['value'])
                asset = self.env['account.asset.asset'].create(vals)
            if self.asset_category_id.open_asset:
                asset.validate()
        return True
