
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError
from openerp.exceptions import Warning as UserError


class AccountCheckDepositExtend(models.Model):
    _inherit = "account.check.deposit"
                
    @api.model
    def _prepare_counterpart_move_lines_vals(
            self, deposit, total_debit, total_amount_currency):
        return {
            'name': _('Check Deposit %s') % deposit.name,
            'debit': total_debit,
            'credit': 0.0,
#             'account_id': deposit.company_id.check_deposit_account_id.id,
            'account_id': deposit.partner_bank_id.journal_id.default_debit_account_id.id,
            'partner_id': False,
            'currency_id': deposit.currency_none_same_company_id.id or False,
            'amount_currency': total_amount_currency,
            }

    @api.multi
    def validate_deposit(self):
        am_obj = self.env['account.move']
        aml_obj = self.env['account.move.line']
        for deposit in self:
            move_vals = self._prepare_account_move_vals(deposit)
            move = am_obj.create(move_vals)
            total_debit = 0.0
            total_amount_currency = 0.0
            to_reconcile_lines = []
            for line in deposit.check_payment_ids:
                total_debit += line.debit
                total_amount_currency += line.amount_currency
                line_vals = self._prepare_move_line_vals(line)
                line_vals['move_id'] = move.id
                move_line = aml_obj.create(line_vals)
                to_reconcile_lines.append(line + move_line)
                line.write({'is_depositedtobank':True})

            # Create counter-part
            if not deposit.partner_bank_id.journal_id:
                raise UserError(
                    _("Missing Account for Check Deposits on the "
                        "company '%s'.") % deposit.company_id.name)

            counter_vals = self._prepare_counterpart_move_lines_vals(
                deposit, total_debit, total_amount_currency)
            counter_vals['move_id'] = move.id
            aml_obj.create(counter_vals)

            move.post()
            deposit.write({'state': 'deposit', 'move_id': move.id})
            # We have to reconcile after post()
            for reconcile_lines in to_reconcile_lines:
                reconcile_lines.reconcile()
        return True