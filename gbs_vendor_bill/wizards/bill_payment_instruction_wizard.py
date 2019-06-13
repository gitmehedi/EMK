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
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True,
                                        default=lambda self: self.env.context.get('op_unit'))
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sub Operating Unit')

    @api.constrains('amount')
    def _check_amount(self):
        for line in self:
            rem_amount = self.env.context.get('invoice_amount')
            if line.amount > rem_amount:
                raise ValidationError(_("Sorry! This amount is bigger then remaining balance. "
                                        "Remaining balance is %s") % (rem_amount))

    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        if self.invoice_id:
            operating_unit_ids = [i.operating_unit_id.id for i in self.invoice_id.invoice_line_ids]
            sub_operating_unit_ids = [i.sub_operating_unit_id.id for i in self.invoice_id.invoice_line_ids]
            return {'domain': {
                'operating_unit_id': [('id', 'in', operating_unit_ids)],
                'sub_operating_unit_id': [('id', 'in', sub_operating_unit_ids)]
            }}

    # @api.onchange('operating_unit_id')
    # def _onchange_operating_unit_id(self):
    #     if self.operating_unit_id:
    #         sub_operating_unit_ids = self.env['sub.operating.unit'].search([('operating_unit_id','=',self.operating_unit_id.id)])
    #         return {'domain': {
    #             'sub_operating_unit_id': [('id', 'in', sub_operating_unit_ids)]
    #         }}

    @api.multi
    def action_validate(self):
        for line in self.invoice_id.suspend_security().move_id.line_ids:
            if line.account_id.internal_type in ('receivable', 'payable'):
                if line.amount_residual < 0:
                    val = -1
                else:
                    val = 1
                line.write({'amount_residual': ((line.amount_residual) * val) - self.amount})

        credit_acc = credit_acc_id = False
        account_config_pool = self.env['account.config.settings'].sudo().search([], order='id desc', limit=1)
        if self.invoice_id.partner_id.vendor_bank_acc:
            credit_acc = self.invoice_id.partner_id.vendor_bank_acc
        elif account_config_pool and account_config_pool.sundry_account_id:
            credit_acc_id = account_config_pool.sundry_account_id
        else:
            raise UserError(
                _("Account Settings are not properly set. "
                  "Please contact your system administrator for assistance."))

        self.env['payment.instruction'].create({
            'invoice_id': self.invoice_id.id,
            'partner_id': self.invoice_id.partner_id.id,
            'currency_id': self.invoice_id.currency_id.id,
            'default_debit_account_id': self.invoice_id.partner_id.property_account_payable_id.id,
            'default_credit_account_id': credit_acc_id.id if credit_acc_id else None,
            'vendor_bank_acc': credit_acc,
            'instruction_date': self.instruction_date,
            'amount': self.amount,
            'operating_unit_id': self.operating_unit_id.id or None,
            'sub_operating_unit_id': self.sub_operating_unit_id.id if self.sub_operating_unit_id else None,
        })
        return {'type': 'ir.actions.act_window_close'}
