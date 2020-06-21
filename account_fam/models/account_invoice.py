# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    is_asset = fields.Boolean(default=False)

    @api.multi
    def do_merge(self, keep_references=True, date_invoice=False):
        res = super(AccountInvoice, self).do_merge(keep_references=keep_references, date_invoice=date_invoice)
        if res:
            if True in [i.is_asset for i in self]:
                self.browse(res).write({'is_asset': True})
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    asset_category_id = fields.Many2one('account.asset.category', string='Asset Type', ondelete="restrict")
    asset_type_id = fields.Many2one('account.asset.category', string='Asset Category', ondelete="restrict")
    asset_name = fields.Char(string='Asset Name')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        vals = super(AccountInvoiceLine, self)._onchange_product_id()
        if self.product_id:
            self.asset_name = self.product_id.name
        return vals

    @api.onchange('asset_type_id')
    def onchange_asset_type_id(self):
        if self.invoice_id.type == 'out_invoice' and self.asset_type_id:
            self.account_id = self.asset_type_id.asset_suspense_account_id.id
        elif self.invoice_id.type == 'in_invoice' and self.asset_type_id:
            self.account_id = self.asset_type_id.asset_suspense_account_id.id

    @api.one
    def asset_create(self):
        if self.asset_category_id:
            asset_value = self.price_subtotal / self.quantity
            batch_seq = {val: key for key, val in enumerate(self.invoice_id.invoice_line_ids.ids)}
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
                    'operating_unit_id': self.invoice_id.operating_unit_id.id,
                    'current_branch_id': self.invoice_id.operating_unit_id.id,
                    'prorata': True,
                    'batch_no': "{0}-{1}".format(self.invoice_id.number, batch_seq[self.id]),
                    'cost_centre_id': self.account_analytic_id.id if self.account_analytic_id else None,
                }

                changed_vals = self.env['account.asset.asset'].onchange_category_id_values(vals['category_id'])
                vals.update(changed_vals['value'])
                asset = self.env['account.asset.asset'].create(vals)
            if self.asset_category_id.open_asset:
                asset.validate()
        return True
