from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def invoice_line_move_line_get(self):
        res = []
        for line in self.invoice_line_ids:
            if line.quantity == 0:
                continue
            tax_ids = []
            for tax in line.invoice_line_tax_ids:
                tax_ids.append((4, tax.id, None))
                for child in tax.children_tax_ids:
                    if child.type_tax_use != 'none':
                        tax_ids.append((4, child.id, None))
            analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]

            if line.invoice_line_tax_ids and line.invoice_line_tax_ids[0].rebate:
                price = line.price_subtotal_without_vat
            else:
                price = line.price_subtotal
            move_line_dict = {
                'invl_id': line.id,
                'type': 'src',
                'name': line.name.split('\n')[0][:64] if line.name else False,
                'price_unit': line.price_unit,
                'quantity': line.quantity,
                'price': price,
                'account_id': line.account_id.id,
                'product_id': line.product_id.id,
                'uom_id': line.uom_id.id,
                'account_analytic_id': line.account_analytic_id.id,
                'tax_ids': tax_ids,
                'invoice_id': self.id,
                'analytic_tag_ids': analytic_tag_ids
            }
            res.append(move_line_dict)
        return res

    @api.model
    def tax_line_move_line_get(self):
        res = []
        # keep track of taxes already processed
        done_taxes = []
        # loop the invoice.tax.line in reversal sequence
        for tax_line in sorted(self.tax_line_ids, key=lambda x: -x.sequence):
            tax = tax_line.tax_id
            if tax_line.amount:
                if tax.amount_type == "group":
                    for child_tax in tax.children_tax_ids:
                        done_taxes.append(child_tax.id)
                if self.vat_selection in ['mushok', 'vds_authority'] and tax_line.tax_id:
                    amount = tax_line.mushok_vds_amount
                else:
                    amount = tax_line.amount
                if tax_line.tax_id:
                    tax_type = 'vat'
                else:
                    tax_type = 'tds'
                res.append({
                    'invoice_tax_line_id': tax_line.id,
                    'tax_line_id': tax_line.tax_id.id,
                    'type': 'tax',
                    'name': tax_line.name,
                    'price_unit': -amount,
                    'quantity': 1,
                    'price': -amount,
                    'account_id': tax_line.account_id.id,
                    'product_id': tax_line.product_id.id,
                    'account_analytic_id': tax_line.account_analytic_id.id,
                    'invoice_id': self.id,
                    'operating_unit_id': tax_line.operating_unit_id.id,
                    'is_tdsvat_payable': self.type in ('out_invoice', 'in_invoice') and True,
                    'tax_type': tax_type,
                    'tax_ids': [(6, 0, list(done_taxes))] if tax_line.tax_id.include_base_amount else []
                })
                done_taxes.append(tax.id)

            if tax_line.tax_id.rebate:
                if self.vat_selection in ['mushok', 'vds_authority'] and tax_line.tax_id \
                        and tax_line.mushok_vds_amount > 0.0:
                    rebate_amount = tax_line.mushok_vds_amount
                else:
                    rebate_amount = tax_line.amount
                res.append({
                    'invoice_tax_line_id': tax_line.id,
                    'tax_line_id': tax_line.tax_id.id,
                    'type': 'tax',
                    'name': tax_line.name,
                    'price_unit': rebate_amount,
                    'quantity': 1,
                    'price': rebate_amount,
                    'account_id': tax_line.tax_id.rebate_account_id.id,
                    'product_id': tax_line.product_id.id,
                    'account_analytic_id': tax_line.account_analytic_id.id,
                    'invoice_id': self.id,
                    'operating_unit_id': tax_line.operating_unit_id.id,
                    # 'is_tdsvat_payable': self.type in ('out_invoice', 'in_invoice') and True,
                    'is_tdsvat_payable': False,
                    # 'tax_type': 'vat',
                    'tax_ids': [(6, 0, list(done_taxes))] if tax_line.tax_id.include_base_amount else []
                })
                done_taxes.append(tax.id)
        return res