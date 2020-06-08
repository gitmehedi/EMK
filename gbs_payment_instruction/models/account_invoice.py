from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'ir.needaction_mixin']

    payment_line_ids = fields.One2many('payment.instruction', 'invoice_id', string='Payment')
    total_payment_amount = fields.Float('Total Payment', compute='_compute_payment_amount',
                                        store=True, readonly=True, track_visibility='onchange', copy=False)
    total_payment_approved = fields.Float('Approved Payment', compute='_compute_payment_amount',
                                          store=True, readonly=True, track_visibility='onchange', copy=False)
    payment_approver = fields.Text('Payment Instruction Responsible', track_visibility='onchange',
                                   help="Log for payment approver", copy=False)
    payment_btn_visible = fields.Boolean(compute='_compute_payment_btn_visible', default=False,
                                         string="Is Visible")

    @api.one
    @api.depends('payment_line_ids.amount', 'payment_line_ids.state')
    def _compute_payment_amount(self):
        for invoice in self:
            invoice.total_payment_amount = sum(
                line.amount for line in invoice.payment_line_ids if line.state not in ['cancel'])
            invoice.total_payment_approved = sum(
                line.amount for line in invoice.payment_line_ids if line.state in ['approved'])

    @api.depends('payable_to_supplier', 'total_payment_amount')
    def _compute_payment_btn_visible(self):
        for record in self:
            if record.state == 'open':
                if record.payable_to_supplier and record.total_payment_amount \
                        and record.payable_to_supplier <= record.total_payment_amount:
                    record.payment_btn_visible = False
                else:
                    record.payment_btn_visible = True
            else:
                record.payment_btn_visible = False

    def action_payment_instruction(self):
        # if self.residual <= 0.0:
        #     raise ValidationError(_('There is no remaining balance for this Bill!'))
        #
        # if self.residual <= sum(line.amount for line in self.payment_line_ids if line.state == 'draft'):
        #     raise ValidationError(_('Without Approval/Rejection of previous payment instruction'
        #                             ' no new payment instruction can possible!'))

        res = self.env.ref('gbs_payment_instruction.view_bill_payment_instruction_wizard')

        return {
            'name': _('Payment Instruction'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'bill.payment.instruction.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {
                'amount': self.payable_to_supplier - self.total_payment_amount or 0.0,
                'currency_id': self.currency_id.id or False,
                'op_unit': self.operating_unit_id.id or False,
                'partner_id': self.partner_id.id or False,
                'debit_acc': self.partner_id.property_account_payable_id.id,
                'partner_id': self.partner_id.id
                # 'sub_op_unit': self.invoice_line_ids[0].sub_operating_unit_id.id if self.invoice_line_ids[
                #     0].sub_operating_unit_id else None,
            }
        }