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
        if ac_move_ids:
            if self.reverse_option == 'op1':
                return self.env['account.move'].browse(ac_move_ids.ids).reverse_moves(date, journal_id or False)
            else:
                return self.custom_reverse_move(date, journal_id or False, ac_move_ids, ac_move_line_ids)
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def custom_reverse_move(self, date=None, journal_id=None,move_id=None,ac_move_line_ids=None):
        reversed_move = move_id.copy(default={
            'date': date,
            'journal_id': journal_id.id if journal_id else self.journal_id.id,
            'ref': _('reversal of: ') + move_id.name})
        tax_grouped = {}
        for ac_move_line_id in ac_move_line_ids:
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

        return reversed_move.post()

# elif self.reverse_option == 'op1' and acc_invoice.payment_line_ids:
# for payment_line_id in acc_invoice.payment_line_ids:
#     if payment_line_id.state == 'approved':
#         self.env['payment.instruction'].create({
#             'invoice_id': self.acc_invoice.id,
#             'partner_id': self.acc_invoice.partner_id.id,
#             'currency_id': self.acc_invoice.currency_id.id,
#             'default_debit_account_id': payment_line_id.default_credit_account_id and payment_line_id.default_credit_account_id.id,
#             'default_credit_account_id': payment_line_id.default_debit_account_id and payment_line_id.default_debit_account_id.id,
#             'vendor_bank_acc': payment_line_id.vendor_bank_acc,
#             'instruction_date': date,
#             'amount': payment_line_id.amount,
#             'operating_unit_id': payment_line_id.operating_unit_id.id or None,
#             'sub_operating_unit_id': payment_line_id.sub_operating_unit_id.id if payment_line_id.sub_operating_unit_id else None,
#         })
# return self.env['account.move'].browse(ac_move_ids.ids).reverse_moves(date, journal_id or False)