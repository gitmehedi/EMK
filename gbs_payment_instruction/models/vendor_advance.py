from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class VendorAdvance(models.Model):
    _name = 'vendor.advance'
    _inherit = ['vendor.advance', 'ir.needaction_mixin']

    payment_line_ids = fields.One2many('payment.instruction', 'advance_id', string='Payment')
    total_payment_amount = fields.Float('Total Payment', compute='_compute_payment_amount',
                                        store=True, readonly=True, track_visibility='onchange', copy=False)
    total_payment_approved = fields.Float('Approved Payment', compute='_compute_payment_amount',
                                          store=True, readonly=True, track_visibility='onchange', copy=False)
    payment_btn_visible = fields.Boolean(compute='_compute_payment_btn_visible', default=False,
                                         string="Is Visible")

    @api.one
    @api.depends('payment_line_ids.amount', 'payment_line_ids.state')
    def _compute_payment_amount(self):
        for advance in self:
            advance.total_payment_amount = sum(
                line.amount for line in advance.payment_line_ids if line.state not in ['cancel'])
            advance.total_payment_approved = sum(
                line.amount for line in advance.payment_line_ids if line.state in ['approved'])

    @api.depends('payable_to_supplier', 'total_payment_amount')
    def _compute_payment_btn_visible(self):
        for record in self:
            if record.state == 'approve':
                if record.payable_to_supplier and record.total_payment_amount \
                        and record.payable_to_supplier <= record.total_payment_amount:
                    record.payment_btn_visible = False
                elif record.payable_to_supplier <= 0.0:
                    record.payment_btn_visible = False
                else:
                    record.payment_btn_visible = True
            else:
                record.payment_btn_visible = False

    @api.multi
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
                'advance_id': self.id,
                'payment_type': 'advance',
                'sub_op_unit': self.sub_operating_unit_id.id or False
            }
        }