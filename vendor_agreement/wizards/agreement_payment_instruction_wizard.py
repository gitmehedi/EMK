from odoo import models, fields, api,_
from odoo.exceptions import UserError,ValidationError


class AgreementPaymentInstructionWizard(models.TransientModel):
    _name = 'agreement.payment.instruction.wizard'

    agreement_id = fields.Many2one('agreement', default=lambda self: self.env.context.get('active_id'),
                                 string="Agreement", copy=False, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.context.get('currency_id'))
    amount = fields.Float(string='Remaining Amount', required=True,
                          default=lambda self: self.env.context.get('amount'))
    advance_amount = fields.Float(string='Advance Amount', readonly=True,
                          default=lambda self: self.env.context.get('advance_amount'))
    total_payment_approved = fields.Float(string='Paid Amount', readonly=True,
                          default=lambda self: self.env.context.get('total_payment_approved'))
    instruction_date = fields.Date(string='Date', default=fields.Date.context_today,
                                   required=True, copy=False)
    credit_account_id = fields.Many2one('account.account', string='Credit Account',
                                        required=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Branch',
                                        default=lambda self: self.env['res.users'].
                                        operating_unit_default_get(self._uid))
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sub Operating Unit')

    @api.constrains('amount')
    def _check_amount(self):
        for line in self:
            rem_amount = self.env.context.get('amount')
            if line.amount > rem_amount:
                raise ValidationError(_("Sorry! This amount is bigger then remaining balance. "
                                        "Remaining balance is %s")% (rem_amount))

    @api.multi
    def action_confirm(self):
        debit_acc = False
        debit_acc_id = False
        account_config_pool = self.env.user.company_id
        if self.agreement_id.partner_id.vendor_bank_acc:
            debit_acc = self.agreement_id.partner_id.vendor_bank_acc
        elif account_config_pool and account_config_pool.sundry_account_id:
            debit_acc_id = account_config_pool.sundry_account_id
        else:
            raise UserError(
                _("Account Settings are not properly set. "
                  "Please contact your system administrator for assistance."))

        self.env['payment.instruction'].create({
            'agreement_id': self.agreement_id.id,
            'partner_id': self.agreement_id.partner_id.id,
            'currency_id': self.currency_id.id,
            'vendor_bank_acc': debit_acc,
            'default_debit_account_id': debit_acc_id.id if debit_acc_id else None,
            'default_credit_account_id': self.credit_account_id.id,
            'instruction_date': self.instruction_date,
            'amount': self.amount,
            'operating_unit_id': self.operating_unit_id.id,
            'sub_operating_unit_id': self.sub_operating_unit_id.id,
        })
        return {'type': 'ir.actions.act_window_close'}