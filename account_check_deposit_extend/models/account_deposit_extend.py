# -*- coding: utf-8 -*-
###############################################################################
#
#   account_check_deposit for Odoo
#   Copyright (C) 2012-2015 Akretion (http://www.akretion.com/)
#   @author: Benoît GUILLOT <benoit.guillot@akretion.com>
#   @author: Chafique DELLI <chafique.delli@akretion.com>
#   @author: Alexis de Lattre <alexis.delattre@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

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
            deposit.write({'state': 'done', 'move_id': move.id})
            # We have to reconcile after post()
            for reconcile_lines in to_reconcile_lines:
                reconcile_lines.reconcile()
        return True