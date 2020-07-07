from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class RentPaymentInstructionWizard(models.TransientModel):
    _name = 'rent.payment.instruction.wizard'

    def default_rent_agreement(self):
        rent_id = self.env.context.get('active_id', False)
        agreement = self.env['agreement'].browse(rent_id)
        return agreement

    def default_rent_lines(self):
        rent_id = self.env.context.get('active_id', False)
        agreement = self.env['agreement'].browse(rent_id)
        lines = []
        for line in agreement.line_ids:
            vals = {
                'currency_id': line.currency_id.id,
                'amount': line.adjustment_value,
                'advance_amount': line.advance_amount,
                'total_payment_approved': line.advance_amount,
                'debit_operating_unit_id': line.line_id.operating_unit_id.id,
                'credit_operating_unit_id': line.line_id.operating_unit_id.id,
                'partner_id': line.partner_id.id,
                'vendor_bank_acc': line.partner_id.vendor_bank_acc,
                'type': 'casa',
                'agreement_line_id': line.line_id.operating_unit_id.id,
            }

            lines.append(vals)

        return lines

    rent_id = fields.Many2one('agreement', string="Agreement", default=default_rent_agreement)
    line_ids = fields.One2many('rent.payment.instruction.line.wizard', 'line_id', default=default_rent_lines)

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


class RentPaymentInstructionLineWizard(models.TransientModel):
    _name = 'rent.payment.instruction.line.wizard'

    line_id = fields.Many2one('rent.payment.instruction.wizard', string='Currency', required=True)
    agreement_line_id = fields.Many2one('agreement.line', string='Agreement Line', required=True)

    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    amount = fields.Float(string='Amount', required=True)
    advance_amount = fields.Float(string='Approved Amount', readonly=True)
    total_payment_approved = fields.Float(string='Advance Paid', readonly=True)
    instruction_date = fields.Date(string='Date', default=fields.Date.context_today, required=True, copy=False)
    credit_account_id = fields.Many2one('account.account', string='Credit Account')
    debit_operating_unit_id = fields.Many2one('operating.unit', string='Debit Branch')
    credit_operating_unit_id = fields.Many2one('operating.unit', string='Credit Branch')
    credit_sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Credit Sequence')
    debit_sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Debit Sequence')
    partner_id = fields.Many2one('res.partner', string='Vendor')
    type = fields.Selection([('casa', 'CASA'), ('credit', 'Credit Account')], default='casa', string='Payment To')
    vendor_bank_acc = fields.Char(related='partner_id.vendor_bank_acc', string='Vendor Bank Account')
    narration = fields.Char(string='Narration', size=30, required=True)

    @api.onchange('type')
    def _onchange_type(self):
        agreement_id = self.line_id.rent_id.id
        agreement_line_id = self.line_id.rent_id.id

        if self.type=='credit':
            self.vendor_bank_acc=''
            self.partner_id=''
            self.credit_account_id=self.credit_account_id
            self.vendor_bank_acc=''
        else:
            self.partner_id = ''
            self.vendor_bank_acc = ''

            self.credit_account_id = self.credit_account_id
            self.vendor_bank_acc = ''

