from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    def create_exchange_rate_entry(self, aml_to_fix, amount_diff, diff_in_currency, currency, move_date):
        """ Automatically create a journal entry to book the exchange rate difference.
            That new journal entry is made in the company `currency_exchange_journal_id` and one of its journal
            items is matched with the other lines to balance the full reconciliation.
        """
        for rec in self:
            if not rec.company_id.currency_exchange_journal_id:
                raise UserError(_("You should configure the 'Exchange Rate Journal' in the accounting settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))
            if not rec.company_id.income_currency_exchange_account_id.id:
                raise UserError(_("You should configure the 'Gain Exchange Rate Account' in the accounting settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))
            if not rec.company_id.expense_currency_exchange_account_id.id:
                raise UserError(_("You should configure the 'Loss Exchange Rate Account' in the accounting settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))
            move_vals = {'journal_id': rec.company_id.currency_exchange_journal_id.id}

            # The move date should be the maximum date between payment and invoice (in case
            # of payment in advance). However, we should make sure the move date is not
            # recorded after the end of year closing.
            if move_date > rec.company_id.fiscalyear_lock_date:
                move_vals['date'] = move_date
            move = rec.env['account.move'].create(move_vals)
            amount_diff = rec.company_id.currency_id.round(amount_diff)
            diff_in_currency = currency.round(diff_in_currency)
            line_to_reconcile = rec.env['account.move.line'].with_context(check_move_validity=False).create({
                'name': _('Currency exchange rate difference'),
                'debit': amount_diff < 0 and -amount_diff or 0.0,
                'credit': amount_diff > 0 and amount_diff or 0.0,
                'account_id': rec.debit_move_id.account_id.id,
                'move_id': move.id,
                'currency_id': currency.id,
                'amount_currency': -diff_in_currency,
                'partner_id': rec.debit_move_id.partner_id.id,
            })
            rec.env['account.move.line'].create({
                'name': _('Currency exchange rate difference'),
                'debit': amount_diff > 0 and amount_diff or 0.0,
                'credit': amount_diff < 0 and -amount_diff or 0.0,
                'account_id': amount_diff > 0 and rec.company_id.currency_exchange_journal_id.default_debit_account_id.id or rec.company_id.currency_exchange_journal_id.default_credit_account_id.id,
                'move_id': move.id,
                'currency_id': currency.id,
                'amount_currency': diff_in_currency,
                'partner_id': rec.debit_move_id.partner_id.id,
                'cost_center_id': self.env.context.get('cost_center_id', False),
                'operating_unit_id': self.env.context.get('operating_unit_id', False)
            })
            for aml in aml_to_fix:
                partial_rec = rec.env['account.partial.reconcile'].create({
                    'debit_move_id': aml.credit and line_to_reconcile.id or aml.id,
                    'credit_move_id': aml.debit and line_to_reconcile.id or aml.id,
                    'amount': abs(aml.amount_residual),
                    'amount_currency': abs(aml.amount_residual_currency),
                    'currency_id': currency.id,
                })
            move.post()
        return line_to_reconcile, partial_rec

    # Do not forwardport in master as of 2017-07-20
    def _fix_multiple_exchange_rates_diff(self, amls_to_fix, amount_diff, diff_in_currency, currency, move):
        self.ensure_one()
        move_lines = self.env['account.move.line'].with_context(check_move_validity=False)
        partial_reconciles = self.with_context(skip_full_reconcile_check=True)
        amount_diff = self.company_id.currency_id.round(amount_diff)
        diff_in_currency = currency.round(diff_in_currency)

        for aml in amls_to_fix:
            account_payable_line = move_lines.create({
                'name': _('Currency exchange rate difference'),
                'debit': amount_diff < 0 and -aml.amount_residual or 0.0,
                'credit': amount_diff > 0 and aml.amount_residual or 0.0,
                'account_id': self.debit_move_id.account_id.id,
                'move_id': move.id,
                'currency_id': currency.id,
                'amount_currency': -aml.amount_residual_currency,
                'partner_id': self.debit_move_id.partner_id.id,
            })

            move_lines.create({
                'name': _('Currency exchange rate difference'),
                'debit': amount_diff > 0 and aml.amount_residual or 0.0,
                'credit': amount_diff < 0 and -aml.amount_residual or 0.0,
                'account_id': amount_diff > 0 and self.company_id.currency_exchange_journal_id.default_debit_account_id.id or self.company_id.currency_exchange_journal_id.default_credit_account_id.id,
                'move_id': move.id,
                'currency_id': currency.id,
                'amount_currency': aml.amount_residual_currency,
                'partner_id': self.debit_move_id.partner_id.id,
                'cost_center_id': self.env.context.get('cost_center_id', False),
                'operating_unit_id': self.env.context.get('operating_unit_id', False)})

            partial_rec = super(AccountPartialReconcile, partial_reconciles).create({
                    'debit_move_id': aml.credit and account_payable_line.id or aml.id,
                    'credit_move_id': aml.debit and account_payable_line.id or aml.id,
                    'amount': abs(aml.amount_residual),
                    'amount_currency': abs(aml.amount_residual_currency),
                    'currency_id': currency.id,
            })

            move_lines |= account_payable_line
            partial_reconciles |= partial_rec

        partial_reconciles._compute_partial_lines()
        return move_lines, partial_reconciles
