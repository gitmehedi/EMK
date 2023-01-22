from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class VendorAdvance(models.Model):
    _name = 'vendor.security.return'
    _inherit = ['vendor.security.return', 'ir.needaction_mixin']

    payment_line_ids = fields.One2many('payment.instruction', 'security_return_id', string='Payment')
    total_payment_amount = fields.Float('Total Payment', compute='_compute_payment_amount',
                                        store=True, readonly=True, track_visibility='onchange', copy=False)
    total_payment_approved = fields.Float('Approved Payment', compute='_compute_payment_amount',
                                          store=True, readonly=True, track_visibility='onchange', copy=False)
    payment_btn_visible = fields.Boolean(compute='_compute_payment_btn_visible', default=False,
                                         string="Is Visible")
    amount_due = fields.Float(string='Amount Due', compute='_compute_amount_due', readonly=True, copy=False, store=True)

    @api.depends('amount', 'total_payment_approved', 'state')
    def _compute_amount_due(self):
        for rec in self:
            if rec.state == 'approve':
                rec.amount_due = rec.amount - rec.total_payment_approved
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

    @api.depends('amount', 'total_payment_amount')
    def _compute_payment_btn_visible(self):
        for record in self:
            if record.state == 'approve':
                if round(record.amount, 2) <= round(record.total_payment_amount, 2):
                    record.payment_btn_visible = False
                else:
                    record.payment_btn_visible = True
            else:
                record.payment_btn_visible = False

    @api.multi
    def action_payment_instruction(self):
        # ou_id = [deposit.operating_unit_id.id for deposit in self.vsd_ids][0]
        op_unit = self.env['operating.unit'].search([('code', '=', '001')], limit=1)

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
                'amount': round(self.amount - self.total_payment_amount, 2) or 0.0,
                'currency_id': self.currency_id.id or False,
                # 'op_unit': ou_id or False,
                'op_unit': op_unit.id or False,
                'partner_id': self.partner_id.id or False,
                'debit_acc': self.partner_id.property_account_payable_id.id,
                'security_return_id': self.id,
                'payment_type': 'security_return',
                'sub_op_unit': self.partner_id.property_account_payable_sou_id.id or False
            }
        }