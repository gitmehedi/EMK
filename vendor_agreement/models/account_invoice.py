# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    agreement_adjusted_amount = fields.Float('Agreement Adjusted Amount',
                                             store=True, readonly=True, track_visibility='onchange')

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        if self.agreement_id and self.agreement_id.active == True \
                and self.date >= self.agreement_id.start_date and self.date <= self.agreement_id.end_date:
            self.update_move_lines_with_agreement(move_lines)
        return move_lines

    def update_move_lines_with_agreement(self, move_lines):
        if self.agreement_id.advance_amount > self.agreement_id.adjusted_amount:
            remaining_amount = self.agreement_id.advance_amount - self.agreement_id.adjusted_amount
            if remaining_amount >= self.agreement_id.adjustment_value:
                amount = self.agreement_id.adjustment_value
            else:
                amount = remaining_amount
        else:
            amount = 0.0
        if amount:
            move_lines[-1][2]['credit'] = move_lines[-1][2]['credit'] - amount
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
            self.agreement_adjusted_amount = amount

        self.agreement_id.write({'adjusted_amount': self.agreement_id.adjusted_amount + amount})

        return True