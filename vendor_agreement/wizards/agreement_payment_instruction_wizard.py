from odoo import models, fields, api,_
from odoo.exceptions import UserError,ValidationError


class AgreementPaymentInstructionWizard(models.TransientModel):
    _name = 'agreement.payment.instruction.wizard'

    agreement_id = fields.Many2one('agreement', default=lambda self: self.env.context.get('active_id'),
                                 string="Agreement", copy=False, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.context.get('currency_id'))
    amount = fields.Float(string='Amount', required=True,
                          default=lambda self: self.env.context.get('amount'))
    instruction_date = fields.Date(string='Date', default=fields.Date.context_today,
                                   required=True, copy=False)

    @api.constrains('amount')
    def _check_amount(self):
        for line in self:
            rem_amount = self.env.context.get('amount')
            if line.amount > rem_amount:
                raise ValidationError(_("Sorry! This amount is bigger then remaining balance. "
                                        "Remaining balance is %s")% (rem_amount))

    @api.multi
    def action_confirm(self):
        credit_acc = credit_acc_id = False
        account_config_pool = self.env['account.config.settings'].sudo().search([], order='id desc', limit=1)
        if self.agreement_id.partner_id.vendor_bank_acc:
            credit_acc = self.agreement_id.partner_id.vendor_bank_acc
        elif account_config_pool and account_config_pool.sundry_account_id:
            credit_acc_id = account_config_pool.sundry_account_id
        else:
            raise UserError(
                _("Account Settings are not properly set. "
                  "Please contact your system administrator for assistance."))

        self.env['payment.instruction'].create({
            'agreement_id': self.agreement_id.id,
            'partner_id': self.agreement_id.partner_id.id,
            'currency_id': self.currency_id.id,
            'vendor_bank_acc': credit_acc,
            'default_debit_account_id': self.agreement_id.partner_id.property_account_payable_id.id,
            'default_credit_account_id': credit_acc_id.id if credit_acc_id else None,
            'instruction_date': self.instruction_date,
            'amount': self.amount,
        })
        return {'type': 'ir.actions.act_window_close'}