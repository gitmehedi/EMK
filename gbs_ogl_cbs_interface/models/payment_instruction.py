from odoo import models, fields, api, _, tools, SUPERUSER_ID
from odoo.exceptions import ValidationError


class PaymentInstruction(models.Model):
    _inherit = 'payment.instruction'
    _payments = []

    @api.multi
    def action_approve(self):
        if not self.move_id.report_process:
            raise ValidationError(
                _("The originating journal [{0}] yet to sync in CBS. Please try later.".format(self.move_id.name)))

        payment = self.search([('id', '=', self.id), ('is_sync', '=', False), ('state', '=', 'draft')])
        if not payment:
            raise ValidationError(_("Payment Instruction [{0}] already submitted.".format(self.code)))
        if payment.state == 'draft' and not payment.is_sync and payment.code not in self._payments:
            if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
                raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))

            self._payments.append(self.code)
            api_ins = self.env['soap.process']
            recon_cr = self.default_credit_account_id.reconcile
            recon_dr = self.default_debit_account_id.reconcile

            if recon_cr or recon_dr:
                if self.vendor_bank_acc:
                    response = api_ins.call_glto_deposit_transfer(payment)
                else:
                    response = api_ins.call_glto_gl_transfer(payment)
            else:
                response = api_ins.call_generic_transfer_amount(payment)

            if 'error_code' in response:
                self.payment_remove(self.code)
                err_text = "Payment of {0} is not possible due to following reason:\n\n - Error Code: {1} \n - Error Message: {2}".format(
                    self.code, response['error_code'], response['error_message'])
                raise ValidationError(_(err_text))
            elif response == 'OkMessage':
                payment.write({'state': 'approved'})
                if payment.invoice_id:
                    for line in payment.invoice_id.suspend_security().move_id.line_ids:
                        if line.account_id.internal_type in ('receivable', 'payable'):
                            if line.amount_residual < 0:
                                val = -1
                            else:
                                val = 1
                            line.write({'amount_residual': ((line.amount_residual) * val) - payment.amount})
                self.payment_remove(self.code)
            else:
                self.payment_remove(self.code)
        else:
            raise ValidationError(_("Payment Instruction [{0}] is processing.".format(self.code)))

    @api.multi
    def payment_remove(self, code):
        if code in self._payments:
            self._payments.remove(code)

    @api.multi
    def invalidate_payment_cache(self):
        payments = self.search([('is_sync', '=', False), ('state', '=', 'draft')])
        for val in payments:
            if val.code in self._payments:
                self._payments.remove(val.code)
