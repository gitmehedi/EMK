from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import re


class BillPaymentInstructionWizard(models.TransientModel):
    _name = 'bill.payment.instruction.wizard'

    invoice_id = fields.Many2one('account.invoice', default=lambda self: self.env.context.get('invoice_id'),
                                 string="Invoice", copy=False, readonly=True)
    advance_id = fields.Many2one('vendor.advance', default=lambda self: self.env.context.get('advance_id'),
                                 string="Advance", copy=False)
    security_return_id = fields.Many2one('vendor.security.return',
                                         default=lambda self: self.env.context.get('security_return_id'),
                                         string='Security Return', copy=False)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.context.get('currency_id'))
    amount = fields.Float(string='Amount', required=True, default=lambda self: self.env.context.get('amount'),
                          digits=(16, 2))
    instruction_date = fields.Date(string='Date', default=fields.Date.context_today, required=True, copy=False)

    debit_operating_unit_id = fields.Many2one('operating.unit', string='Debit Branch', required=True,
                                              default=lambda self: self.env.context.get('op_unit'))
    debit_sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Debit Sequence',
                                                  default=lambda self: self.env.context.get('sub_op_unit'))
    partner_id = fields.Many2one('res.partner', string='Vendor',
                                 default=lambda self: self.env.context.get('partner_id'))
    vendor_bank_acc = fields.Char(string='Vendor Bank Account', related='partner_id.vendor_bank_acc', size=13)
    type = fields.Selection([('casa', 'CASA'), ('credit', 'Credit Account')], default='casa', string='Payment To')
    credit_account_id = fields.Many2one('account.account', string='Credit Account')
    credit_operating_unit_id = fields.Many2one('operating.unit', string='Credit Branch')
    credit_sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Credit Sequence')
    narration = fields.Char(string="Narration", size=30, required=True)
    debit_account_id = fields.Many2one('account.account', string='Debit Account',
                                       default=lambda self: self.env.context.get('debit_acc'))
    payment_type = fields.Selection([('invoice', "Invoice"),
                                     ('advance', "Advance"),
                                     ('security_return', "Security Return")], string="Payment Type",
                                    default=lambda self: self.env.context.get('payment_type'))
    advance_type = fields.Selection([('single', "Single"),
                                     ('multi', "Multi")
                                     ], string='Advance Type', related='advance_id.type')

    credit_operating_unit_domain_ids = fields.Many2many('operating.unit',
                                                        compute="_compute_credit_operating_unit_domain_ids",
                                                        readonly=True, store=False)

    @api.constrains('narration')
    def _check_narration(self):
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')

        if regex.search(self.narration) != None:
            raise ValidationError(_("Following special character is not allowed [@_!#$%^&*()<>?/\|}{~:]"))

    @api.multi
    @api.depends('credit_sub_operating_unit_id')
    def _compute_credit_operating_unit_domain_ids(self):
        for rec in self:
            if rec.credit_sub_operating_unit_id.all_branch:
                rec.credit_operating_unit_domain_ids = self.env['operating.unit'].search([])
            else:
                rec.credit_operating_unit_domain_ids = rec.credit_sub_operating_unit_id.branch_ids

    @api.onchange('credit_sub_operating_unit_id')
    def _onchange_credit_sub_operating_unit_id(self):
        for rec in self:
            rec.credit_operating_unit_id = None

    @api.constrains('amount')
    def _check_amount(self):
        for line in self:
            rem_amount = self.env.context.get('amount')
            if line.amount <= 0:
                raise ValidationError(_("Amount should be more than zero (0)."))
            elif line.amount > rem_amount:
                raise ValidationError(_("Sorry! This amount is bigger than remaining balance. "
                                        "Remaining balance is %s") % (rem_amount))

    @api.onchange('credit_account_id')
    def _onchange_account_id(self):
        for rec in self:
            rec.credit_sub_operating_unit_id = None

    @api.multi
    def action_validate(self):
        # debit_acc = self.invoice_id.partner_id.property_account_payable_id.id
        remaining = self.env.context.get('amount')
        if self.invoice_id:
            remaining = round(self.invoice_id.amount_payable - self.invoice_id.total_payment_amount, 2)
        elif self.advance_id:
            if not self.advance_id.is_bulk_data:
                remaining = round(self.advance_id.payable_to_supplier - self.advance_id.total_payment_amount, 2)
            else:
                remaining = round(self.advance_id.additional_advance_amount - self.advance_id.total_payment_amount, 2)
        elif self.security_return_id:
            remaining = round(self.security_return_id.amount - self.security_return_id.total_payment_amount, 2)
        if self.amount > remaining:
            raise ValidationError(
                "This amount is bigger than remaining balance.The remaining balance is {}".format(abs(remaining)))

        debit_branch = self.debit_operating_unit_id.id or None
        if self.debit_sub_operating_unit_id:
            debit_sou = self.debit_sub_operating_unit_id.id
        else:
            raise ValidationError("[Configuration Error] Please configure sequence for the following Vendor in account "
                                  "configuration:\n {}".format(self.partner_id.name))
        # partner_id = self.invoice_id.partner_id.id

        if self.type == 'casa':
            vendor_bank_acc = self.vendor_bank_acc
            credit_acc = False
            credit_branch = False
            credit_sou = False
        if self.type == 'credit':
            vendor_bank_acc = False
            credit_acc = self.credit_account_id.id
            credit_branch = self.credit_operating_unit_id.id
            credit_sou = self.credit_sub_operating_unit_id.id if self.credit_sub_operating_unit_id else None

        if self.invoice_id.id:
            # generate reconcile ref code (Vendor Bills)
            reconcile_ref = self.invoice_id.get_reconcile_ref(self.debit_account_id.id, self.invoice_id.id)
            move_id = self.invoice_id.move_id.id
        elif self.advance_id:

            # generate reconcile ref code (Vendor Advances or Vendor Security Returns)
            ref_code = self.advance_id.name #or self.security_return_id.name
            if len(self.advance_id.move_ids) > 1:
                ref_code += str(len(self.advance_id.move_ids) - 1)
            reconcile_ref = self.advance_id.get_reconcile_ref(self.debit_account_id.id, ref_code)
            move_id = self.advance_id.move_ids[0].id
        elif self.security_return_id:
            ref_code = self.security_return_id.name
            reconcile_ref = self.env['vendor.advance'].get_reconcile_ref(self.debit_account_id.id, ref_code)
            move_id = self.security_return_id.move_id.id
        else:
            reconcile_ref = None
            move_id = False

        # move_id = self.invoice_id.move_id.id or self.advance_id.journal_id.id or self.security_return_id.move_id.id or False

        self.env['payment.instruction'].create({
            'invoice_id': self.invoice_id.id or False,
            'advance_id': self.advance_id.id or False,
            'security_return_id': self.security_return_id.id or False,
            'instruction_date': self.env.user.company_id.batch_date,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'default_debit_account_id': self.debit_account_id.id,
            'debit_operating_unit_id': debit_branch,
            'debit_sub_operating_unit_id': debit_sou,
            'partner_id': self.partner_id.id,
            'vendor_bank_acc': vendor_bank_acc,
            'default_credit_account_id': credit_acc,
            'credit_operating_unit_id': credit_branch,
            'credit_sub_operating_unit_id': credit_sou,
            'narration': self.narration,
            'reconcile_ref': reconcile_ref,
            'move_id': move_id
        })
        return {'type': 'ir.actions.act_window_close'}
