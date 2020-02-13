from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class RentPaymentInstructionWizard(models.TransientModel):
    _name = 'rent.payment.instruction.wizard'

    # def default_rent_agreement(self):
    #     rent_id = self.env.context.get('active_id', False)
    #     agreement = self.env['agreement'].browse(rent_id)
    #     return agreement

    rent_id = fields.Many2one('agreement', string="Agreement")

    @api.constrains('amount')
    def _check_amount(self):
        for line in self:
            rem_amount = self.env.context.get('amount')
            if line.amount > rem_amount:
                raise ValidationError(_("Sorry! This amount is bigger then remaining balance. "
                                        "Remaining balance is %s") % (rem_amount))

    @api.multi
    def action_confirm(self):
        debit_acc = self.agreement_id.account_id.id
        debit_branch = self.debit_operating_unit_id.id or None
        debit_sou = self.debit_sub_operating_unit_id.id if self.debit_sub_operating_unit_id else None

        if self.type == 'casa':
            vendor_bank_acc = self.partner_id.vendor_bank_acc
            credit_acc = False
            credit_branch = False
            credit_sou = False
        if self.type == 'credit':
            vendor_bank_acc = False
            credit_acc = self.credit_account_id.id
            credit_branch = self.credit_operating_unit_id.id
            credit_sou = self.credit_sub_operating_unit_id.id if self.credit_sub_operating_unit_id else None

        self.env['payment.instruction'].create({
            'agreement_id': self.agreement_id.id,
            'instruction_date': self.instruction_date,
            'amount': self.amount,
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'default_debit_account_id': debit_acc,
            'debit_operating_unit_id': debit_branch,
            'debit_sub_operating_unit_id': debit_sou,
            'vendor_bank_acc': vendor_bank_acc,
            'default_credit_account_id': credit_acc,
            'credit_operating_unit_id': credit_branch,
            'credit_sub_operating_unit_id': credit_sou,
            'narration': self.narration,
        })
        return {'type': 'ir.actions.act_window_close'}
