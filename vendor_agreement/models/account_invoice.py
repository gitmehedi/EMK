# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    agreement_id = fields.Many2one('agreement', string='Agreement', ondelete='restrict',
                                   readonly=True, states={'draft': [('readonly', False)]},
                                   track_visibility='onchange', copy=False)

    agreement_adjusted_amount = fields.Float('Adjusted Amount', compute='_compute_agreement_adjusted_amount',
                                             store=True, readonly=True,
                                             track_visibility='onchange', copy=False)

    @api.one
    @api.depends('invoice_line_ids')
    def _compute_agreement_adjusted_amount(self):
        for invoice in self:
            if invoice.invoice_line_ids and invoice.agreement_id.product_id in [i.product_id for i in invoice.invoice_line_ids]:
                if invoice.agreement_id.total_payment_approved > invoice.agreement_id.adjusted_amount:
                    remaining_amount = invoice.agreement_id.total_payment_approved - invoice.agreement_id.adjusted_amount
                    if remaining_amount >= invoice.agreement_id.adjustment_value:
                        invoice.agreement_adjusted_amount = invoice.agreement_id.adjustment_value
                    else:
                        invoice.agreement_adjusted_amount = remaining_amount
                else:
                    invoice.agreement_adjusted_amount = 0.0

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        move_lines = super(AccountInvoice,self).finalize_invoice_move_lines(move_lines)
        if self.agreement_id and self.agreement_id.active == True \
                and self.date >= self.agreement_id.start_date and self.date <= self.agreement_id.end_date:
            self.update_move_lines_with_agreement(move_lines,self.agreement_adjusted_amount)
        return move_lines

    def update_move_lines_with_agreement(self, move_lines,amount):
        if amount:
            for line in move_lines:
                if line[2]['name'] == '/':
                    line[2]['credit'] = line[2]['credit'] - amount
            agreement_values = {
                'account_id': self.agreement_id.account_id.id,
                'analytic_account_id': self.invoice_line_ids[0].account_analytic_id.id,
                'credit': amount,
                'date_maturity': self.date_due,
                'debit': False,
                'invoice_id': self.id,
                'name': self.agreement_id.name,
                'operating_unit_id': self.operating_unit_id.id,
                'partner_id': self.partner_id.id,
                'agreement_id': self.agreement_id.id,
            }
            move_lines.append((0, 0, agreement_values))

        self.agreement_id.write({'adjusted_amount': self.agreement_id.adjusted_amount + amount})

        return True

    @api.model
    def _get_invoice_key_cols(self):
        res = super(AccountInvoice, self)._get_invoice_key_cols()
        res.append('agreement_id')
        return res

    @api.model
    def _get_first_invoice_fields(self, invoice):
        res = super(AccountInvoice, self)._get_first_invoice_fields(invoice)
        res.update({'agreement_id': invoice.agreement_id.id or False})
        return res
