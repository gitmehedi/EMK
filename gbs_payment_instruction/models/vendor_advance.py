from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class VendorAdvance(models.Model):
    _name = 'vendor.advance'
    _inherit = ['vendor.advance', 'ir.needaction_mixin']

    payment_line_ids = fields.One2many('payment.instruction', 'advance_id', string='Payment', copy=False)
    total_payment_amount = fields.Float('Total Payment', compute='_compute_payment_amount',
                                        store=True, readonly=True, track_visibility='onchange', copy=False)
    total_payment_approved = fields.Float('Total Approved Payment', compute='_compute_payment_amount',
                                          store=True, readonly=True, track_visibility='onchange', copy=False)
    payment_btn_visible = fields.Boolean(compute='_compute_payment_btn_visible', default=False, copy=False,
                                         string="Is Visible")
    is_bulk_data = fields.Boolean(default=False, copy=False, string="Is a Bulk Data")
    amount_due = fields.Float(string='Amount Due', compute='_compute_amount_due', readonly=True, copy=False, store=True)

    @api.depends('payable_to_supplier', 'total_payment_approved', 'additional_advance_amount', 'is_bulk_data', 'state')
    def _compute_amount_due(self):
        for rec in self:
            if rec.state == 'approve':
                if not rec.is_bulk_data:
                    rec.amount_due = rec.payable_to_supplier - rec.total_payment_approved
                else:
                    rec.amount_due = rec.additional_advance_amount - rec.total_payment_approved
            else:
                rec.amount_due = 0.0

    @api.one
    @api.depends('payment_line_ids.amount', 'payment_line_ids.state')
    def _compute_payment_amount(self):
        for advance in self:
            advance.total_payment_amount = sum(
                line.amount for line in advance.payment_line_ids if line.state not in ['cancel'])
            advance.total_payment_approved = sum(
                line.amount for line in advance.payment_line_ids if line.state in ['approved'])

    @api.depends('payable_to_supplier', 'total_payment_amount', 'is_bulk_data', 'type', 'additional_advance_amount')
    def _compute_payment_btn_visible(self):
        for record in self:
            if record.state == 'approve':
                if not record.is_bulk_data:
                    if round(record.payable_to_supplier, 2) <= round(record.total_payment_amount, 2):
                        record.payment_btn_visible = False
                    elif record.payable_to_supplier <= 0.0:
                        record.payment_btn_visible = False
                    else:
                        record.payment_btn_visible = True
                else:
                    if record.type == 'single':
                        record.payment_btn_visible = False
                    else:
                        if round(record.additional_advance_amount, 2) <= round(record.total_payment_amount, 2):
                            record.payment_btn_visible = False
                        else:
                            record.payment_btn_visible = True
            else:
                record.payment_btn_visible = False

    @api.multi
    def action_payment_instruction(self):
        res = self.env.ref('gbs_payment_instruction.view_bill_payment_instruction_wizard')
        op_unit = self.env['operating.unit'].search([('code', '=', '001')], limit=1)
        if not self.is_bulk_data:
            amount = round(self.payable_to_supplier - self.total_payment_amount, 2) or 0.0
        else:
            amount = round(self.additional_advance_amount - self.total_payment_amount, 2) or 0.0

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
                'amount': amount,
                'currency_id': self.currency_id.id or False,
                # 'op_unit': self.operating_unit_id.id or False,
                'op_unit': op_unit.id or False,
                'partner_id': self.partner_id.id or False,
                'debit_acc': self.partner_id.property_account_payable_id.id,
                'advance_id': self.id,
                'payment_type': 'advance',
                'sub_op_unit': self.partner_id.property_account_payable_sou_id.id or False
            }
        }