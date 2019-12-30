from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountInvoiceReverse(models.TransientModel):
    """Reverse invoice"""
    _name = "account.invoice.reverse"

    @api.model
    def _default_option(self):
        if self._context.get('active_id'):
            move_lines = self.env['account.move.line'].search([('invoice_id','=',self._context.get('active_id')),
                                                               ('tax_type','in',('tds','vat'))])
            ilist = [i for i in move_lines if i.pending_for_paid or i.is_paid or i.is_challan]
            if ilist:
                return 'op2'
        return 'op1'

    reverse_option = fields.Selection([
        ('op1', 'Option 1'),
        ('op2', 'Option 2')], string='Reverse Option',default=_default_option)

    @api.multi
    def invoice_reverse(self):
        date = fields.Date.context_today(self)
        journal_id = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
        ac_move_line_ids = self.env['account.move.line'].search([('invoice_id', '=', self._context.get('active_id'))])
        ac_move_ids = self.env['account.move'].search([('id', '=', ac_move_line_ids and ac_move_line_ids[0].move_id.id)])
        acc_invoice = ac_move_line_ids[0].mapped('invoice_id')
        if acc_invoice.state in ("open","paid") and ac_move_ids:
            if self.reverse_option == 'op1' and not acc_invoice.payment_line_ids:
                self.env['account.move'].browse(ac_move_ids.ids).reverse_moves(date, journal_id or False)
                return acc_invoice.write({'state': 'cancel', 'move_id': False})
            elif self.reverse_option == 'op2' and not acc_invoice.payment_line_ids:
                return self.custom_reverse_move(date, journal_id or False, ac_move_ids, ac_move_line_ids)
            elif self.reverse_option == 'op1' and acc_invoice.payment_line_ids:
                self.reverse_payment_instruction(date,acc_invoice)
                self.env['account.move'].browse(ac_move_ids.ids).reverse_moves(date, journal_id or False)
                return acc_invoice.write({'state': 'cancel', 'move_id': False,'payment_line_ids':[(3, acc_invoice.payment_line_ids.ids)]})
            else:
                self.reverse_payment_instruction(date,acc_invoice)
                self.custom_reverse_move(date, journal_id or False, ac_move_ids, ac_move_line_ids)
                return acc_invoice.write({'state': 'cancel', 'move_id': False,'payment_line_ids':[(3, acc_invoice.payment_line_ids.ids)]})
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def custom_reverse_move(self, date=None, journal_id=None,move_id=None,ac_move_line_ids=None):
        reversed_move = move_id.copy(default={
            'date': date,
            'journal_id': journal_id.id if journal_id else self.journal_id.id,
            'ref': _('reversal of: ') + move_id.name})
        tax_grouped = {}
        for ac_move_line_id in ac_move_line_ids:
            # need to change this condition
            if ac_move_line_id.pending_for_paid or ac_move_line_id.is_paid or ac_move_line_id.is_challan:
                val = ac_move_line_id.credit
                key = ac_move_line_id.product_id.id

                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key] += val

        for move_line_id in reversed_move.line_ids:
            if move_line_id.debit:
                if move_line_id.product_id.id in tax_grouped:
                    move_line_id.debit -= tax_grouped[move_line_id.product_id.id]
                    del tax_grouped[move_line_id.product_id.id]
                move_line_id.write({
                    'debit': move_line_id.credit,
                    'credit': move_line_id.debit,
                    'amount_currency': -move_line_id.amount_currency,
                })
            elif move_line_id.pending_for_paid or move_line_id.is_paid or move_line_id.is_challan:
                move_line_id.unlink()
            else:
                move_line_id.write({
                    'debit': move_line_id.credit,
                    'credit': move_line_id.debit,
                    'amount_currency': -move_line_id.amount_currency,
                    'is_tdsvat_payable': False
                })

        return reversed_move.sudo().post()

    @api.multi
    def reverse_payment_instruction(self, date=None, acc_invoice=None):
        for payment_line_id in acc_invoice.payment_line_ids:
            if payment_line_id.state == 'approved':
                new_payment_instruction_obj = self.env['payment.instruction'].create({
                    'invoice_id': acc_invoice.id,
                    'partner_id': acc_invoice.partner_id.id,
                    'currency_id': acc_invoice.currency_id.id,
                    'default_debit_account_id': payment_line_id.default_credit_account_id and payment_line_id.default_credit_account_id.id,
                    'default_credit_account_id': payment_line_id.default_debit_account_id and payment_line_id.default_debit_account_id.id,
                    'vendor_bank_acc': payment_line_id.vendor_bank_acc or False,
                    'instruction_date': date,
                    'state': 'approved',
                    'amount': payment_line_id.amount,
                    'credit_operating_unit_id': payment_line_id.debit_operating_unit_id.id or None,
                    'debit_operating_unit_id': payment_line_id.credit_operating_unit_id.id or None,
                    'credit_sub_operating_unit_id': payment_line_id.debit_sub_operating_unit_id.id if payment_line_id.debit_sub_operating_unit_id else None,
                    'debit_sub_operating_unit_id': payment_line_id.credit_sub_operating_unit_id.id if payment_line_id.credit_sub_operating_unit_id else None,
                    'origin': payment_line_id.id or False,
                })
                new_payment_instruction_obj.action_invoice_reverse()
        return True