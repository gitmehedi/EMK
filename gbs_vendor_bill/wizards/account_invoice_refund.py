# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountInvoiceRefund(models.TransientModel):
    """Refunds invoice"""
    _inherit = "account.invoice.refund"

    filter_refund = fields.Selection([('refund', 'Create a draft refund'), ('cancel', 'Cancel: create refund and reconcile')],
        default='refund', string='Refund Method', required=True, help='Refund base on this type. You can not Modify and Cancel if the invoice is already reconciled')


    @api.multi
    def compute_refund(self, mode='refund'):
        res = super(AccountInvoiceRefund, self).compute_refund(mode='refund')
        if res:
            account_invoice = self.env['account.invoice'].browse(self._context.get('active_ids'))
            if account_invoice:
                account_moves = self.env['account.move.line'].search([('invoice_id', '=', account_invoice.id)])
                for account_move in account_moves:
                    if account_move.is_tdsvat_payable is True:
                        account_move.is_tdsvat_payable = False

                if account_invoice.payment_line_ids:
                    for payment_line in account_invoice.payment_line_ids:
                        if payment_line.state == 'approved':
                            raise UserError(_(
                                'Cannot refund this invoice which has payment instruct approved.'))
                        else:
                            payment_line.unlink()
        return res

