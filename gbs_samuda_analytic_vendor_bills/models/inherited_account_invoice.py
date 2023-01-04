import json
from odoo import fields, models, api, _
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import UserError, ValidationError


class InheritedAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    ############# custom compute field just to show tds and vds ###############

    @api.depends('tax_line_ids')
    def calculate_tds_value(self):
        for rec in self:
            rec.tds_value = 0
            if rec.tax_line_ids:
                total_tds = 0
                for line in rec.tax_line_ids:
                    if not line.is_vat:
                        total_tds = total_tds + line.amount
                rec.tds_value = total_tds

    tds_value = fields.Monetary(string='TDS & Other Adjustment', store=False, readonly=True,
                                compute='calculate_tds_value')

    @api.depends('tax_line_ids')
    def calculate_vds_value(self):
        for rec in self:
            rec.vat_payable_value = 0
            if rec.tax_line_ids:
                total_vds = 0
                for line in rec.tax_line_ids:
                    if line.is_vat:
                        total_vds = total_vds + line.amount
                rec.vat_payable_value = total_vds

    vat_payable_value = fields.Monetary(string='VAT Payable', store=False, readonly=True, compute='calculate_vds_value')

    def _prepare_invoice_line_from_po_line(self, line):
        """ Override parent's method to add lc analytic account on invoice line"""
        invoice_line = super(InheritedAccountInvoice, self)._prepare_invoice_line_from_po_line(line)

        if self.type == 'in_invoice' and self.purchase_id:
            if self.purchase_id.region_type == 'foreign' or self.purchase_id.is_service_order:
                if self.purchase_id.lc_ids:
                    analytic_account_id = self.purchase_id.lc_ids[0].analytic_account_id.id
                    if analytic_account_id:
                        invoice_line.update({'account_analytic_id': analytic_account_id})  # update the dictionary
            elif self.purchase_id.cnf_quotation:
                analytic_account_id = self.purchase_id.shipment_id.lc_id.analytic_account_id.id
                if analytic_account_id:
                    invoice_line.update({'account_analytic_id': analytic_account_id})  # update the dictionary

            if self.purchase_id.region_type == 'foreign':
                account_conf_pool = self.env.user.company_id
                if not account_conf_pool.lc_pad_account:

                    raise UserError(
                        _("LC Goods In Transit Account not set. Please contact your system administrator for "
                          "assistance."))
                invoice_line.update({'account_id': account_conf_pool.lc_pad_account.id})  # update the dictionary
       
        return invoice_line
