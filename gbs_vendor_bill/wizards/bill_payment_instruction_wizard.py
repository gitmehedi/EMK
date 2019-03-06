from odoo import models, fields, api,_
from odoo.exceptions import UserError,ValidationError


class BillPaymentInstructionWizard(models.TransientModel):
    _name = 'bill.payment.instruction.wizard'

    def _get_amount(self):
        return self.env.context.get('invoice_amount') - self.env.context.get('instructed_amount')

    invoice_id = fields.Many2one('account.invoice', default=lambda self: self.env.context.get('active_id'),
                                 string="Invoice", copy=False, readonly=True)
    amount = fields.Float(string='Amount', required=True,default=_get_amount)
    invoice_amount = fields.Float(string='Invoice Amount', required=True,readonly=True,
                                  default=lambda self: self.env.context.get('invoice_amount'))
    instruction_date = fields.Date(string='Date', default=fields.Date.context_today,
                                   required=True, copy=False)
    instructed_amount = fields.Float(readonly=True,default=lambda self: self.env.context.get('instructed_amount'))

    @api.constrains('amount')
    def _check_amount(self):
        for line in self:
            rem_amount = line.invoice_amount - line.instructed_amount
            if line.amount > rem_amount:
                raise ValidationError(_("Sorry! This amount is bigger then remaining balance."
                                        "Remaining balance is %s")% (rem_amount))

    @api.multi
    def action_validate(self):
        self.env['payment.instruction'].create({
            'invoice_id': self.invoice_id.id,
            'partner_id': self.invoice_id.partner_id.id,
            'currency_id': self.invoice_id.currency_id.id,
            'default_debit_account_id': self.invoice_id.partner_id.property_account_payable_id.id,
            'default_credit_account_id': self.invoice_id.partner_id.property_account_receivable_id.id,
            'instruction_date': self.instruction_date,
            'amount': self.amount,
        })
        return {'type': 'ir.actions.act_window_close'}