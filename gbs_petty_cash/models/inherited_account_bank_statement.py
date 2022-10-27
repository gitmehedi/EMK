# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import time


class InheritedAccountBankStatement(models.Model):
    _name = 'account.bank.statement'
    _inherit = ['account.bank.statement', 'mail.thread']

    @api.model
    def create(self, vals):
        if 'line_ids' in vals:
            if not vals['line_ids']:
                raise UserError(
                    _('Transaction lines cannot be empty!'))

        if 'temp_journal_id' in vals and 'is_petty_cash_journal' in vals:
            journal_id = vals['temp_journal_id']
            is_petty_cash_journal = vals['is_petty_cash_journal']
            if is_petty_cash_journal:
                statements = self.env['account.bank.statement'].search(
                    [('journal_id', '=', journal_id), ('state', '=', 'open')])
                if statements:
                    raise UserError(
                        _('Please reconcile and validate previous transactions for this journal.\n Then you can create new transaction!'))

        if 'balance_start_duplicate' in vals and 'line_ids' in vals:
            total = 0
            for line in vals['line_ids']:
                amount = float(line[2]['amount'])
                total = total + amount
            if float(vals['balance_start_duplicate']) + total < 0:
                raise UserError('Ending Balance can not be Negative!')
            vals['balance_end_real'] = float(vals['balance_start_duplicate']) + total
        return super(InheritedAccountBankStatement, self).create(vals)

    @api.multi
    def write(self, values):
        if 'line_ids' in values:
            line_len = len(values['line_ids'])
            total = 0
            sum_to_deduct = 0
            for x in xrange(line_len):
                # if changing existing line amount
                if values['line_ids'][x][2]:
                    if values['line_ids'][x][1] and 'amount' in values['line_ids'][x][2]:
                        bank_statement_line = self.env['account.bank.statement.line'].browse(values['line_ids'][x][1])
                        if bank_statement_line:
                            sum_to_deduct = sum_to_deduct + bank_statement_line.amount
                    if 'amount' in values['line_ids'][x][2]:
                        amount = float(values['line_ids'][x][2]['amount'])
                        total = total + amount
            if sum_to_deduct < 0:
                total = total + (-1) * sum_to_deduct
            else:
                total = total - sum_to_deduct
            if total + self.balance_end_real < 0:
                raise UserError('Ending Balance can not be Negative!')

            values['balance_end_real'] = total + self.balance_end_real
        res = super(InheritedAccountBankStatement, self).write(values)
        if not self.line_ids:
            raise UserError(
                _('Transaction lines cannot be empty!'))

        return res

    @api.model
    def _default_opening_balance(self):
        # Search last bank statement and set current opening balance as closing balance of previous one
        journal_id = self._context.get('default_journal_id', False) or self._context.get('journal_id', False)
        if journal_id:
            return self._get_opening_balance(journal_id)
        return 0

    balance_start = fields.Monetary(string='Starting Balance', default=_default_opening_balance)
    balance_start_duplicate = fields.Monetary(string='Start Balance', default=_default_opening_balance)

    @api.depends('journal_id')
    def get_temp_journal(self):
        for rec in self:
            if rec.journal_id:
                rec.temp_journal_id = rec.journal_id.id

    temp_journal_id = fields.Many2one('account.journal', string='Journal', readonly=False, compute='get_temp_journal')

    name = fields.Char(string='Reference', size=60, states={'open': [('readonly', False)]}, copy=False, readonly=True)

    @api.constrains('balance_start')
    def _check_balance_start_negative_val(self):
        if self.balance_start < 0:
            raise ValidationError('Starting Balance can not be Negative!')

    @api.constrains('difference')
    def _check_amount_val(self):
        if self.difference and self.difference != 0:
            raise ValidationError('End Balance does not match. Difference with real end balance = %s' % self.difference)

    petty_cash_reconciled = fields.Boolean(default=False)

    @api.depends('journal_id')
    def _check_journal(self):
        for rec in self:
            if rec.journal_id:
                if rec.journal_id.petty_cash_journal:
                    rec.is_petty_cash_journal = True
                else:
                    rec.is_petty_cash_journal = False

    is_petty_cash_journal = fields.Boolean(compute="_check_journal", readonly=False)

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

    matched_manual_ids = fields.One2many('account.bank.statement.manual', 'statement_id', "Journal Entry")

    matched_move_line_ids = fields.Many2many('account.move.line', relation='bank_statement_matched_move_line')

    def get_move_line_vals(self, name, date, journal_id, account_id, operating_unit_id, department_id, cost_center_id,
                           debit, credit,
                           company_id, statement_line_id, partner_id, analytic_account_id):
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
                'partner_id': partner_id,
                'analytic_account_id': analytic_account_id
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
                'partner_id': partner_id,
                'analytic_account_id': analytic_account_id
                # 'company_id': company_id,
            }

    def process_move_line_reconciliation(self, statement, matched_move_lines, st_number):

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

        move = self.env['account.move'].suspend_security().create(vals)
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
                                                       self.company_id.id, self.id, aml.partner_id.id, False)

                else:
                    # debit

                    aml_vals = self.get_move_line_vals(aml.name, aml.date, aml.journal_id.id,
                                                       aml.account_id.id,
                                                       aml.journal_id.operating_unit_id.id,
                                                       aml.department_id.id, aml.cost_center_id.id,
                                                       (-1) * aml.amount_residual,
                                                       0,
                                                       self.company_id.id, self.id, aml.partner_id.id, False)
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
                                                       self.company_id.id, self.id, line.partner_id.id, False)
                else:
                    aml_vals = self.get_move_line_vals(line.name, line.date, self.journal_id.id,
                                                       self.journal_id.default_credit_account_id.id,
                                                       self.journal_id.operating_unit_id.id, False, False, 0,
                                                       (-1) * line.amount,
                                                       self.company_id.id, self.id, line.partner_id.id, False)

                aml_vals['move_id'] = move.id
                aml_vals['payment_id'] = payment.id
                new_aml = self.env['account.move.line'].with_context(check_move_validity=False).create(aml_vals)
            move.post()
            if move:
                statement.write({'petty_cash_reconciled': True})
            payment.write({'payment_reference': move.name})
        return True

    @api.multi
    def action_reconcile_stmt(self):
        statement = self.env['account.bank.statement'].browse(self.id)
        context = {'ir_sequence_date': statement.date}
        if statement.journal_id.sequence_id:
            st_number = statement.journal_id.sequence_id.with_context(**context).next_by_id()
            if "OU" in st_number:
                st_number = st_number.replace('OU', statement.journal_id.operating_unit_id.code)
        else:
            raise UserError(_("Petty Cash journal sequence not found!"))
        # matched_move_line
        if self.matched_move_line_ids:
            self.process_move_line_reconciliation(statement, self.matched_move_line_ids, st_number)
        elif self.matched_manual_ids:
            move_lines = []
            for manual_entry in self.matched_manual_ids:
                if manual_entry.balance > 0:
                    # credit
                    aml_vals = self.get_move_line_vals(manual_entry.name, manual_entry.date, statement.journal_id.id,
                                                       manual_entry.account_id.id,
                                                       statement.journal_id.operating_unit_id.id,
                                                       manual_entry.department_id.id, manual_entry.cost_center_id.id, 0,
                                                       manual_entry.balance,
                                                       statement.company_id.id, self.id, manual_entry.partner_id.id,
                                                       manual_entry.analytic_account_id.id)

                else:
                    # debit
                    aml_vals = self.get_move_line_vals(manual_entry.name, manual_entry.date, statement.journal_id.id,
                                                       manual_entry.account_id.id,
                                                       statement.journal_id.operating_unit_id.id,
                                                       manual_entry.department_id.id, manual_entry.cost_center_id.id,
                                                       (-1) * manual_entry.balance,
                                                       0,
                                                       statement.company_id.id, self.id, manual_entry.partner_id.id,
                                                       manual_entry.analytic_account_id.id)

                move_lines.append((0, 0, aml_vals))
            total_amount = 0
            for line in self.line_ids:
                total_amount = total_amount + line.amount

            if total_amount > 0:
                # debit
                aml_vals = self.get_move_line_vals(self.name, self.date, self.journal_id.id,
                                                   self.journal_id.default_debit_account_id.id,
                                                   self.journal_id.operating_unit_id.id, False, False, total_amount,
                                                   0,
                                                   self.company_id.id, self.id, False, False)
            else:
                aml_vals = self.get_move_line_vals(self.name, self.date, self.journal_id.id,
                                                   self.journal_id.default_credit_account_id.id,
                                                   self.journal_id.operating_unit_id.id, False, False, 0,
                                                   (-1) * total_amount,
                                                   self.company_id.id, self.id, False, False)

            move_lines.append((0, 0, aml_vals))

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

                move = self.env['account.move'].suspend_security().create(vals)
                if move:
                    statement.write({'petty_cash_reconciled': True})
        else:
            raise UserError(_("No move line found for reconciliation!"))

    def action_reconcile_all(self):
        self.env.cr.execute(
            'delete from bank_statement_matched_move_line where account_bank_statement_id = %s' % self.id)

        self.env.cr.execute(
            'delete from account_bank_statement_manual where statement_id = %s' % self.id)

        for line in self.line_ids:
            if line.amount == 0:
                raise UserError(_("Transaction amount 0 cannot be taken!"))

            self.env['account.bank.statement.manual'].suspend_security().create({
                'statement_id': self.id,
                'date': line.date,
                'name': line.name,
                'partner_id': line.partner_id.id,
                'balance': line.amount,
                'balance_readonly': line.amount
            })

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
        if not self.petty_cash_reconciled:
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

            if moves:
                moves.filtered(lambda m: m.state != 'posted').post()
            statement.message_post(body=_('Statement %s confirmed, journal items were created.') % (statement.name,))
        statements.link_bank_to_partner()
        statements.write({'state': 'confirm', 'date_done': time.strftime("%Y-%m-%d %H:%M:%S")})

    def duplicate_unreconcile_action(self):
        for st in self:
            if not st.move_line_ids:
                raise UserError(_("Reconciliation not done for this transaction!"))

            moves_to_cancel = st.move_line_ids.mapped('move_id')
            payment_to_cancel = self.env['account.payment']
            # check if reconciles entries exist in move
            for move in moves_to_cancel:
                for line in move.line_ids:
                    payment_to_cancel |= line.payment_id

                move.line_ids.remove_move_reconcile()
                moves_to_cancel.button_cancel()
                moves_to_cancel.unlink()
                if payment_to_cancel:
                    payment_to_cancel.unlink()

                # if reconcile entries found existing invoice matching number set to False
            st.write({'petty_cash_reconciled': False})

    @api.multi
    def action_statement_print(self):
        return self.env['report'].get_action(self, report_name='gbs_petty_cash.petty_cash_report_xlsx')

    @api.multi
    def button_cancel(self):
        for statement in self:
            if statement.is_petty_cash_journal:
                if statement.move_line_ids:
                    raise UserError(_('A statement cannot be canceled when its lines are reconciled.'))
            else:
                if any(line.journal_entry_ids.ids for line in statement.line_ids):
                    raise UserError(_('A statement cannot be canceled when its lines are reconciled.'))

        self.state = 'open'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(InheritedAccountBankStatement, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu)
        if toolbar:
            actions_in_toolbar = res['toolbar'].get('action')
            if actions_in_toolbar:
                temp_actions_in_toolbar = actions_in_toolbar
                for action in temp_actions_in_toolbar:
                    if action['xml_id'] == "account.action_cash_box_in":
                        res['toolbar']['action'].remove(action)
        return res

    @api.multi
    def button_draft(self):
        if self.temp_journal_id and self.is_petty_cash_journal:
            statements = self.env['account.bank.statement'].search(
                [('journal_id', '=', self.temp_journal_id.id), ('state', '=', 'open')])
            if statements:
                raise UserError(
                    _('Please reconcile and validate previous transactions for this journal.\n Then you can create new transaction!'))

        self.state = 'open'
