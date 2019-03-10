from odoo import models, fields, api,_
from odoo.exceptions import UserError,ValidationError


class AgreementPaymentInstructionWizard(models.TransientModel):
    _name = 'agreement.payment.instruction.wizard'

    agreement_id = fields.Many2one('agreement', default=lambda self: self.env.context.get('active_id'),
                                 string="Invoice", copy=False, readonly=True)
    amount = fields.Float(string='Amount', required=True,
                          default=lambda self: self.env.context.get('amount'))
    instruction_date = fields.Date(string='Date', default=fields.Date.context_today,
                                   required=True, copy=False)
    instructed_amount = fields.Float(readonly=True,default=lambda self: self.env.context.get('instructed_amount'))

    @api.constrains('amount')
    def _check_amount(self):
        for line in self:
            rem_amount = self.env.context.get('amount')
            if line.amount > rem_amount:
                raise ValidationError(_("Sorry! This amount is bigger then remaining balance. "
                                        "Remaining balance is %s")% (rem_amount))

    # @api.multi
    # def action_confirm(self):
    #     for line in self.invoice_id.sudo().move_id.line_ids:
    #         if line.account_id.internal_type in ('receivable', 'payable'):
    #             if line.amount_residual<0:
    #                 val = -1
    #             else:
    #                 val = 1
    #             line.write({'amount_residual': ((line.amount_residual)*val)-self.amount})
    #
    #     self.env['payment.instruction'].create({
    #         'invoice_id': self.agreement_id.id,
    #         'partner_id': self.agreement_id.partner_id.id,
    #         'currency_id': self.agreement_id.currency_id.id,
    #         'default_debit_account_id': self.agreement_id.partner_id.property_account_payable_id.id,
    #         'default_credit_account_id': self.agreement_id.partner_id.property_account_receivable_id.id,
    #         'instruction_date': self.instruction_date,
    #         'amount': self.amount,
    #     })
    #     return {'type': 'ir.actions.act_window_close'}