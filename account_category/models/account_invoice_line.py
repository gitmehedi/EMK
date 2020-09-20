# -*- coding: utf-8 -*-

import random

from odoo import api, fields, models, _


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    _asset_recon = []

    asset_type_id = fields.Many2one('account.asset.category', string='Asset Category', ondelete="restrict")

    @api.onchange('asset_category_id')
    def onchange_asset_category_id(self):
        super(AccountInvoiceLine, self).onchange_asset_category_id()
        if self.asset_category_id:
            self.asset_type_id = self.product_id.product_tmpl_id.asset_type_id

    @api.onchange('product_id')
    def _onchange_product_id(self):
        vals = super(AccountInvoiceLine, self)._onchange_product_id()
        if self.product_id:
            if self.invoice_id.type == 'out_invoice':
                self.asset_category_id = self.product_id.product_tmpl_id.deferred_revenue_category_id
            elif self.invoice_id.type == 'in_invoice':
                self.asset_category_id = self.product_id.product_tmpl_id.asset_category_id
                self.asset_type_id = self.product_id.product_tmpl_id.asset_type_id
        return vals

    @api.one
    def asset_create(self):
        if self.asset_category_id and self.asset_type_id:
            asset_value = self.price_total / self.quantity

            batch_seq = {val: key + 1 for key, val in enumerate(self.invoice_id.invoice_line_ids.ids)}
            recon = self.env['account.move.line'].search([('invoice_id', '=', self.invoice_id.id),
                                                          ('product_id', '=', self.product_id.id),
                                                          ('debit', '=', self.price_total)])

            if len(recon) > 1:
                for rec in recon:
                    if rec.reconcile_ref not in self._asset_recon:
                        self._asset_recon.append(rec.reconcile_ref)
                        recoc_ref = rec.reconcile_ref
                        break
                    else:
                        continue
            else:
                recoc_ref = recon.reconcile_ref if recon else ''

            for rec in range(0, int(self.quantity)):
                vals = {
                    'name': self.asset_name or '/',
                    'code': self.invoice_id.number or False,
                    'category_id': self.asset_category_id.id,
                    'asset_type_id': self.asset_type_id.id,
                    'value': asset_value,
                    'depr_base_value': asset_value,
                    'partner_id': self.invoice_id.partner_id.id,
                    'company_id': self.invoice_id.company_id.id,
                    'currency_id': self.invoice_id.company_currency_id.id,
                    'date': self.invoice_id.date_invoice,
                    'invoice_id': self.invoice_id.id,
                    'current_branch_id': self.invoice_id.operating_unit_id.id,
                    'operating_unit_id': self.invoice_id.operating_unit_id.id,
                    'prorata': True,
                    'batch_no': "{0}-{1}".format(self.invoice_id.number, batch_seq[self.id]),
                    'cost_centre_id': self.account_analytic_id.id if self.account_analytic_id else None,
                    'sub_operating_unit_id': self.sub_operating_unit_id.id if self.sub_operating_unit_id else None,
                    'reconcile_ref': recoc_ref
                }
                changed_vals = self.env['account.asset.asset'].onchange_category_id_values(vals['asset_type_id'])
                vals.update(changed_vals['value'])
                asset = self.env['account.asset.asset'].create(vals)
            if self.asset_category_id.open_asset:
                asset.validate()
        return True
