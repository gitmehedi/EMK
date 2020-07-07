from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class BillPaymentInstructionWizard(models.TransientModel):
    _name = 'bill.payment.instruction.wizard'

    invoice_id = fields.Many2one('account.invoice', default=lambda self: self.env.context.get('active_id'),
                                 string="Invoice", copy=False, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.context.get('currency_id'))
    amount = fields.Float(string='Amount', required=True, default=lambda self: self.env.context.get('invoice_amount'))
    instruction_date = fields.Date(string='Date', default=fields.Date.context_today, required=True, copy=False)

    debit_operating_unit_id = fields.Many2one('operating.unit', string='Debit Branch', required=True,
                                              default=lambda self: self.env.context.get('op_unit'))
    debit_sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Debit Sequence')
    partner_id = fields.Many2one('res.partner', string='Vendor',
                                 default=lambda self: self.env.context.get('partner_id'))
    vendor_bank_acc = fields.Char(related='partner_id.vendor_bank_acc', string='Vendor Bank Account')
    type = fields.Selection([('casa', 'CASA'), ('credit', 'Credit Account')], default='casa', string='Payment To')
    credit_account_id = fields.Many2one('account.account', string='Credit Account')
    credit_operating_unit_id = fields.Many2one('operating.unit', string='Credit Branch')
    credit_sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Credit Sequence')
    narration = fields.Char(string="Narration", size=30, required=True)

    @api.constrains('amount')
    def _check_amount(self):
        for line in self:
            rem_amount = self.env.context.get('invoice_amount')
            if line.amount > rem_amount:
                raise ValidationError(_("Sorry! This amount is bigger then remaining balance. "
                                        "Remaining balance is %s") % (rem_amount))

    @api.multi
    def action_validate(self):
        debit_acc = self.invoice_id.partner_id.property_account_payable_id.id
        debit_branch = self.debit_operating_unit_id.id or None
        debit_sou = self.debit_sub_operating_unit_id.id if self.debit_sub_operating_unit_id else None
        partner_id = self.invoice_id.partner_id.id

        if self.type == 'casa':
            vendor_bank_acc = self.invoice_id.partner_id.vendor_bank_acc
            credit_acc = False
            credit_branch = False
            credit_sou = False
        if self.type == 'credit':
            vendor_bank_acc = False
            credit_acc = self.credit_account_id.id
            credit_branch = self.credit_operating_unit_id.id
            credit_sou = self.credit_sub_operating_unit_id.id if self.credit_sub_operating_unit_id else None

        self.env['payment.instruction'].create({
            'invoice_id': self.invoice_id.id,
            'instruction_date': self.instruction_date,
            'amount': self.amount,
            'currency_id': self.invoice_id.currency_id.id,
            'default_debit_account_id': debit_acc,
            'debit_operating_unit_id': debit_branch,
            'debit_sub_operating_unit_id': debit_sou,
            'partner_id': partner_id,
            'vendor_bank_acc': vendor_bank_acc,
            'default_credit_account_id': credit_acc,
            'credit_operating_unit_id': credit_branch,
            'credit_sub_operating_unit_id': credit_sou,
            'narration': self.narration
        })
        return {'type': 'ir.actions.act_window_close'}
