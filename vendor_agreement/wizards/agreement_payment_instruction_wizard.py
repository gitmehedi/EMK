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
    advance_amount = fields.Float(string='Approved Amount', readonly=True,
                          default=lambda self: self.env.context.get('advance_amount'))
    total_payment_approved = fields.Float(string='Advance Paid', readonly=True,
                          default=lambda self: self.env.context.get('total_payment_approved'))
    instruction_date = fields.Date(string='Date', default=fields.Date.context_today,
                                   required=True, copy=False)
    credit_account_id = fields.Many2one('account.account', string='Credit Account',
                                        required=True)
    debit_operating_unit_id = fields.Many2one('operating.unit', string='Debit Branch',
                                              default=lambda self: self.env.context.get('operating_unit_id'))
    credit_operating_unit_id = fields.Many2one('operating.unit', string='Credit Branch',
                                        default=lambda self: self.env['res.users'].
                                        operating_unit_default_get(self._uid))
    credit_sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Credit SOU')
    debit_sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Debit SOU')

    @api.constrains('amount')
    def _check_amount(self):
        for line in self:
            rem_amount = self.env.context.get('amount')
            if line.amount > rem_amount:
                raise ValidationError(_("Sorry! This amount is bigger then remaining balance. "
                                        "Remaining balance is %s")% (rem_amount))

    @api.onchange('credit_operating_unit_id')
    def _onchange_operating_unit_id(self):
        if self.credit_operating_unit_id:
            self.credit_sub_operating_unit_id = []
            credit_sub_operating_unit_ids = self.env['sub.operating.unit'].search([
                ('operating_unit_id', '=', self.credit_operating_unit_id.id)])
            return {'domain': {
                'credit_sub_operating_unit_id': [('id', 'in', credit_sub_operating_unit_ids.ids)]
            }}

    @api.multi
    def action_confirm(self):
        self.env['payment.instruction'].create({
            'agreement_id': self.agreement_id.id,
            'partner_id': self.agreement_id.partner_id.id,
            'currency_id': self.currency_id.id,
            'default_debit_account_id': self.agreement_id.account_id.id,
            'default_credit_account_id': self.credit_account_id.id,
            'instruction_date': self.instruction_date,
            'amount': self.amount,
            'credit_operating_unit_id': self.credit_operating_unit_id.id or None,
            'debit_operating_unit_id': self.debit_operating_unit_id.id or None,
            'credit_sub_operating_unit_id': self.credit_sub_operating_unit_id.id if self.credit_sub_operating_unit_id else None,
            'debit_sub_operating_unit_id': self.debit_sub_operating_unit_id.id if self.debit_sub_operating_unit_id else None,
        })
        return {'type': 'ir.actions.act_window_close'}