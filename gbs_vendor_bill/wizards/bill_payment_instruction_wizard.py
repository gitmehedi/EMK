from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class BillPaymentInstructionWizard(models.TransientModel):
    _name = 'bill.payment.instruction.wizard'

    invoice_id = fields.Many2one('account.invoice', default=lambda self: self.env.context.get('active_id'),
                                 string="Invoice", copy=False, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.context.get('currency_id'))
    amount = fields.Float(string='Amount', required=True,
                          default=lambda self: self.env.context.get('invoice_amount'))
    instruction_date = fields.Date(string='Date', default=fields.Date.context_today,
                                   required=True, copy=False)
    credit_operating_unit_id = fields.Many2one('operating.unit', string='Credit Branch', required=True)
    debit_operating_unit_id = fields.Many2one('operating.unit', string='Debit Branch', required=True,
                                        default=lambda self: self.env.context.get('op_unit'))
    credit_sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Credit SOU')
    debit_sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Debit SOU')
    credit_account_id = fields.Many2one('account.account', string='Credit Account',
                                        required=True)

    @api.constrains('amount')
    def _check_amount(self):
        for line in self:
            rem_amount = self.env.context.get('invoice_amount')
            if line.amount > rem_amount:
                raise ValidationError(_("Sorry! This amount is bigger then remaining balance. "
                                        "Remaining balance is %s") % (rem_amount))

    # @api.onchange('invoice_id')
    # def _onchange_invoice_id(self):
    #     if self.invoice_id:
    #         operating_unit_ids = [i.operating_unit_id.id for i in self.invoice_id.invoice_line_ids]
    #         sub_operating_unit_ids = [i.sub_operating_unit_id.id for i in self.invoice_id.invoice_line_ids]
    #         return {'domain': {
    #             'operating_unit_id': [('id', 'in', operating_unit_ids)],
    #             'sub_operating_unit_id': [('id', 'in', sub_operating_unit_ids)]
    #         }}

    @api.onchange('credit_operating_unit_id')
    def _onchange_operating_unit_id(self):
        if self.credit_operating_unit_id:
            self.credit_sub_operating_unit_id = []
            credit_sub_operating_unit_ids = self.env['sub.operating.unit'].search([
                ('operating_unit_id','=',self.credit_operating_unit_id.id)])
            return {'domain': {
                'credit_sub_operating_unit_id': [('id', 'in', credit_sub_operating_unit_ids.ids)]
            }}


    @api.multi
    def action_validate(self):
        # for line in self.invoice_id.suspend_security().move_id.line_ids:
        #     if line.account_id.internal_type in ('receivable', 'payable'):
        #         if line.amount_residual < 0:
        #             val = -1
        #         else:
        #             val = 1
        #         line.write({'amount_residual': ((line.amount_residual) * val) - self.amount})

        debit_acc = False
        debit_acc_id = False
        account_config_pool = self.env.user.company_id
        if self.invoice_id.partner_id.vendor_bank_acc:
            debit_acc = self.invoice_id.partner_id.vendor_bank_acc
        elif account_config_pool and account_config_pool.sundry_account_id:
            debit_acc_id = self.invoice_id.partner_id.property_account_payable_id.id
        else:
            raise UserError(
                _("Account Settings are not properly set. "
                  "Please contact your system administrator for assistance."))

        self.env['payment.instruction'].create({
            'invoice_id': self.invoice_id.id,
            'partner_id': self.invoice_id.partner_id.id,
            'currency_id': self.invoice_id.currency_id.id,
            'default_debit_account_id': debit_acc_id,
            'default_credit_account_id': self.credit_account_id.id,
            'vendor_bank_acc': debit_acc,
            'instruction_date': self.instruction_date,
            'amount': self.amount,
            'credit_operating_unit_id': self.credit_operating_unit_id.id or None,
            'debit_operating_unit_id': self.debit_operating_unit_id.id or None,
            'credit_sub_operating_unit_id': self.credit_sub_operating_unit_id.id if self.credit_sub_operating_unit_id else None,
            'debit_sub_operating_unit_id': self.debit_sub_operating_unit_id.id if self.debit_sub_operating_unit_id else None,
        })
        return {'type': 'ir.actions.act_window_close'}
