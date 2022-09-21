# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import time


class InheritedAccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    @api.constrains('balance_start')
    def _check_balance_start_negative_val(self):
        if self.balance_start < 0:
            raise ValidationError('Starting Balance can not be Negative')

    @api.constrains('balance_end_real')
    def _check_balance_end_real_negative_val(self):
        if self.balance_end_real < 0:
            raise ValidationError('Ending Balance can not be Negative')

    show_reconcile_button = fields.Boolean(default=True)

    @api.depends('journal_id')
    def _check_journal(self):
        for rec in self:
            if rec.journal_id:
                if rec.journal_id.petty_cash_journal:
                    rec.is_petty_cash_journal = True
                else:
                    rec.is_petty_cash_journal = False

    is_petty_cash_journal = fields.Boolean(compute="_check_journal")

    type_of_operation = fields.Selection([('cash_in', 'Cash In'), ('cash_out', 'Cash Out')], string='Type of Operation')

    @api.depends('line_ids')
    @api.multi
    def _calc_matched_balance(self):
        for record in self:
            total = 0
            for line in record.line_ids:
                total = total + line.amount
            record.matched_balance = total

    matched_balance = fields.Monetary(compute="_calc_matched_balance", string='Open Balance')

    @api.constrains('matched_move_line_ids', 'matched_manual_ids')
    def _check_matched_ids(self):
        if len(self.matched_manual_ids.ids) > 0 and len(self.matched_move_line_ids.ids) > 0:
            raise ValidationError(
                _('Matched move lines and Manual journal entry both have lines! You can input one line betweeen these tabs!'))

    @api.constrains('matched_manual_ids')
    def _check_matched_manual_ids(self):
        if len(self.matched_manual_ids.ids) > 1:
            raise ValidationError(_('You cannot add multiple lines!'))

    matched_manual_ids = fields.One2many('account.bank.statement.manual', 'statement_id')

    @api.constrains('matched_move_line_ids')
    def _check_matched_move_line_ids(self):
        if len(self.matched_move_line_ids.ids) > 1:
            raise ValidationError(_('You cannot add multiple lines!'))

    matched_move_line_ids = fields.Many2many('account.move.line')

    def get_move_line_vals(self, name, date, journal_id, account_id, operating_unit_id, department_id, cost_center_id,
                           debit, credit,
                           company_id, statement_line_id, partner_id):
        if statement_line_id:
            return {
                'name': name,
                'date': date,
                'journal_id': journal_id,
                'account_id': account_id,
                'operating_unit_id': operating_unit_id,
                'department_id': department_id,
                'cost_center_id': cost_center_id,
                'debit': debit,
                'credit': credit,
                'statement_id': statement_line_id,
                'partner_id': partner_id
                # 'company_id': company_id,
            }
        else:
            return {
                'name': name,
                'date': date,
                'journal_id': journal_id,
                'account_id': account_id,
                'operating_unit_id': operating_unit_id,
                'department_id': department_id,
                'cost_center_id': cost_center_id,
                'debit': debit,
                'credit': credit,
                'partner_id': partner_id
                # 'company_id': company_id,
            }

    def process_move_line_reconciliation(self, statement, matched_move_lines):
        context = {'ir_sequence_date': statement.date}
        if statement.journal_id.sequence_id:
            st_number = statement.journal_id.sequence_id.with_context(**context).next_by_id()
            if "OU" in st_number:
                st_number = st_number.replace('OU', statement.journal_id.operating_unit_id.code)
        else:
            raise UserError(_("Petty Cash journal sequence not found!"))

        # create move
        vals = {
            'name': st_number,
            'journal_id': statement.journal_id.id,
            'operating_unit_id': statement.journal_id.operating_unit_id.id,
            'date': statement.date,
            'company_id': statement.company_id.id,
            'state': 'draft',
            'line_ids': False,
            'narration': False,
            'ref': statement.name
        }

        move = self.env['account.move'].create(vals)
        total = self.matched_balance
        if matched_move_lines:
            # Create The payment
            payment = self.env['account.payment']
            if abs(total) > 0.00001:
                payment_methods = (
                                          total > 0) and statement.journal_id.inbound_payment_method_ids or statement.journal_id.outbound_payment_method_ids
                currency = statement.journal_id.currency_id or statement.company_id.currency_id
                payment = self.env['account.payment'].create({
                    'payment_method_id': payment_methods and payment_methods[0].id or False,
                    'payment_type': total > 0 and 'inbound' or 'outbound',
                    'partner_id': False,
                    'journal_id': statement.journal_id.id,
                    'payment_date': statement.date,
                    'state': 'reconciled',
                    'currency_id': currency.id,
                    'amount': abs(total),
                    'communication': False,
                    'name': statement.name or _("Bank Statement %s") % statement.date,
                })

            for aml in matched_move_lines:
                # adding merged move line
                if aml.amount_residual > 0:
                    # credit
                    aml_vals = self.get_move_line_vals(aml.name, aml.date, aml.journal_id.id,
                                                       aml.account_id.id,
                                                       aml.journal_id.operating_unit_id.id,
                                                       aml.department_id.id, aml.cost_center_id.id, 0,
                                                       aml.amount_residual,
                                                       self.company_id.id, self.id, aml.partner_id.id)

                else:
                    # debit

                    aml_vals = self.get_move_line_vals(aml.name, aml.date, aml.journal_id.id,
                                                       aml.account_id.id,
                                                       aml.journal_id.operating_unit_id.id,
                                                       aml.department_id.id, aml.cost_center_id.id,
                                                       (-1) * aml.amount_residual,
                                                       0,
                                                       self.company_id.id, self.id, aml.partner_id.id)
                aml_vals['move_id'] = move.id
                aml_vals['payment_id'] = payment.id
                new_aml = self.env['account.move.line'].with_context(check_move_validity=False).create(aml_vals)
                counterpart_move_line = aml
                (new_aml | counterpart_move_line).reconcile()

            for line in self.line_ids:
                if line.amount > 0:
                    # debit
                    aml_vals = self.get_move_line_vals(line.name, line.date, self.journal_id.id,
                                                       self.journal_id.default_debit_account_id.id,
                                                       self.journal_id.operating_unit_id.id, False, False, line.amount,
                                                       0,
                                                       self.company_id.id, self.id, line.partner_id.id)
                else:
                    aml_vals = self.get_move_line_vals(line.name, line.date, self.journal_id.id,
                                                       self.journal_id.default_credit_account_id.id,
                                                       self.journal_id.operating_unit_id.id, False, False, 0,
                                                       (-1) * line.amount,
                                                       self.company_id.id, self.id, line.partner_id.id)

                aml_vals['move_id'] = move.id
                aml_vals['payment_id'] = payment.id
                new_aml = self.env['account.move.line'].with_context(check_move_validity=False).create(aml_vals)
            move.post()
            if move:
                statement.write({'show_reconcile_button': False})
            payment.write({'payment_reference': move.name})
        return True

    @api.multi
    def action_reconcile_stmt(self):
        statement = self.env['account.bank.statement'].browse(self.id)
        # matched_move_line
        if self.matched_move_line_ids:
            self.process_move_line_reconciliation(statement, self.matched_move_line_ids)
        elif self.matched_manual_ids:
            move_lines = []
            for manual_entry in self.matched_manual_ids:
                if manual_entry.balance > 0:
                    # credit
                    aml_vals = self.get_move_line_vals(manual_entry.name, statement.date, statement.journal_id.id,
                                                       manual_entry.account_id.id,
                                                       statement.journal_id.operating_unit_id.id,
                                                       manual_entry.department_id.id, manual_entry.cost_center_id.id, 0,
                                                       manual_entry.balance,
                                                       statement.company_id.id, self.id, manual_entry.partner_id.id)

                else:
                    # debit
                    aml_vals = self.get_move_line_vals(manual_entry.name, statement.date, statement.journal_id.id,
                                                       manual_entry.account_id.id,
                                                       statement.journal_id.operating_unit_id.id,
                                                       manual_entry.department_id.id, manual_entry.cost_center_id.id,
                                                       (-1) * manual_entry.balance,
                                                       0,
                                                       statement.company_id.id, self.id, manual_entry.partner_id.id)

                move_lines.append((0, 0, aml_vals))
            total_amount = 0
            for line in self.line_ids:
                if line.amount > 0:
                    # debit
                    aml_vals = self.get_move_line_vals(line.name, line.date, self.journal_id.id,
                                                       self.journal_id.default_debit_account_id.id,
                                                       self.journal_id.operating_unit_id.id, False, False, line.amount,
                                                       0,
                                                       self.company_id.id, self.id, line.partner_id.id)
                else:
                    aml_vals = self.get_move_line_vals(line.name, line.date, self.journal_id.id,
                                                       self.journal_id.default_credit_account_id.id,
                                                       self.journal_id.operating_unit_id.id, False, False, 0,
                                                       (-1) * line.amount,
                                                       self.company_id.id, self.id, line.partner_id.id)

                move_lines.append((0, 0, aml_vals))
                total_amount = total_amount + line.amount

            context = {'ir_sequence_date': statement.date}
            if statement.journal_id.sequence_id:
                st_number = statement.journal_id.sequence_id.with_context(**context).next_by_id()
                if "OU" in st_number:
                    st_number = st_number.replace('OU', statement.journal_id.operating_unit_id.code)
            else:
                raise UserError(_("Petty Cash journal sequence not found!"))
            if len(move_lines) > 0:
                vals = {
                    'name': st_number,
                    'journal_id': statement.journal_id.id,
                    'operating_unit_id': statement.journal_id.operating_unit_id.id,
                    'date': statement.date,
                    'company_id': statement.company_id.id,
                    'state': 'draft',
                    'line_ids': move_lines,
                    'narration': False,
                    'ref': statement.name
                }

                move = self.env['account.move'].create(vals)
                if move:
                    statement.write({'show_reconcile_button': False})
        else:
            raise UserError(_("No move line found for reconciliation!"))

    def action_reconcile_all(self):
        ref = lambda name: self.env.ref(name).id
        context = dict(self._context)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Reconciliation'),
            'target': 'new',
            'res_model': 'account.bank.statement',
            'res_id': self.id,
            'view_mode': 'form',
            'views': [(ref('gbs_petty_cash.view_bank_statement_form_reconciliation'), 'form')],
            'context': context
        }

    # duplicate_validate_action
    @api.multi
    def duplicate_validate_action(self):
        if self.show_reconcile_button:
            raise UserError(_("Reconciliation not done!"))
        if self.journal_type == 'cash' and not self.currency_id.is_zero(self.difference):
            action_rec = self.env['ir.model.data'].xmlid_to_object('account.action_view_account_bnk_stmt_check')
            if action_rec:
                action = action_rec.read([])[0]
                return action
        return self.button_confirm_bank_duplicate()

    @api.multi
    def button_confirm_bank_duplicate(self):
        self._balance_check()
        statements = self.filtered(lambda r: r.state == 'open')
        for statement in statements:
            moves = statement.move_line_ids.mapped('move_id')
            # for st_line in statement.line_ids:
            #     if st_line.account_id and not st_line.journal_entry_ids.ids:
            #         st_line.fast_counterpart_creation()
            #     elif not st_line.journal_entry_ids.ids:
            #         raise UserError(
            #             _('All the account entries lines must be processed in order to close the statement.'))
            #     moves = (moves | st_line.journal_entry_ids)

            if moves:
                moves.filtered(lambda m: m.state != 'posted').post()
            statement.message_post(body=_('Statement %s confirmed, journal items were created.') % (statement.name,))
        statements.link_bank_to_partner()
        statements.write({'state': 'confirm', 'date_done': time.strftime("%Y-%m-%d %H:%M:%S")})

    def duplicate_unreconcile_action(self):
        print('Unreconcile button called!')
        # moves_to_cancel = self.env['account.move']
        # payment_to_unreconcile = self.env['account.payment']
        # payment_to_cancel = self.env['account.payment']
        #
        # for st in self:
        #     moves_to_unbind = st.move_line_ids.mapped('move_id')
        #     move_names = moves_to_unbind.mapped('name')
        #     for move in moves_to_unbind:
        #         for line in move.line_ids:
        #             payment_to_unreconcile |= line.payment_id
        #             if line.payment_id.payment_reference in move_names:
        #                 # there can be several moves linked to a statement line but maximum one created by the line itself
        #                 moves_to_cancel |= move
        #                 payment_to_cancel |= line.payment_id
        #
        #     moves_to_unbind = moves_to_unbind - moves_to_cancel
        #
        #
        # for st_line in self:
        #     moves_to_unbind = st_line.journal_entry_ids
        #     for move in st_line.journal_entry_ids:
        #         for line in move.line_ids:
        #             payment_to_unreconcile |= line.payment_id
        #             if st_line.move_name and line.payment_id.payment_reference == st_line.move_name:
        #                 # there can be several moves linked to a statement line but maximum one created by the line itself
        #                 moves_to_cancel |= move
        #                 payment_to_cancel |= line.payment_id
        #
        #     moves_to_unbind = moves_to_unbind - moves_to_cancel
        #
        #     if moves_to_unbind:
        #         moves_to_unbind.write({'statement_line_id': False})
        #         for move in moves_to_unbind:
        #             move.line_ids.filtered(lambda x: x.statement_id == st_line.statement_id).write(
        #                 {'statement_id': False})
        #
        # payment_to_unreconcile = payment_to_unreconcile - payment_to_cancel
        # if payment_to_unreconcile:
        #     payment_to_unreconcile.unreconcile()
        #
        # if moves_to_cancel:
        #     for move in moves_to_cancel:
        #         move.line_ids.remove_move_reconcile()
        #     moves_to_cancel.button_cancel()
        #     moves_to_cancel.unlink()
        # if payment_to_cancel:
        #     payment_to_cancel.unlink()
