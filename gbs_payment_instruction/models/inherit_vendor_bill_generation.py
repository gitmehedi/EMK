from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class VendorBillGeneration(models.Model):
    _inherit = 'vendor.bill.generation'

    state = fields.Selection([
        ('draft', "Pending"),
        ('confirm', "Confirmed"),
        ('approve', "Approved"),
        ('bill_generate', "Bill Generated"),
        ('bill_validate', "Bill Validated"),
        ('cancel', "Canceled"),
        ('payment_done', "Payment Created"),
        ('payment_approve', "Payment Approved")], default='draft', string="Status",
        track_visibility='onchange')
    approve_payment_button_visible = fields.Boolean(compute='_compute_approve_payment_button', default=False)

    @api.depends('line_ids')
    def _compute_approve_payment_button(self):
        for rec in self:
            status_list = [line.payment_instruction_state=='draft' for line in rec.line_ids if line.payment_instruction_id]
            if True in status_list:
                rec.approve_payment_button_visible = True
            else:
                rec.approve_payment_button_visible =False

    @api.multi
    def action_payment(self):
        for rec in self:
            # invoice_ids = self.env['account.invoice'].search([('vbg_batch_id', '=', rec.id)])
            for line in rec.line_ids:
                if line.invoice_id:
                    if line.invoice_id.state == 'open':
                        rec.create_payment_instruction(line)
            rec.write({'state': 'payment_done'})

    @api.multi
    def action_approve_payment(self):
        for rec in self:
            for line in rec.line_ids:
                if line.payment_instruction_id.state == 'draft':
                    try:
                        line.payment_instruction_id.action_approve()
                    except Exception:
                        pass
            rec.write({'state': 'payment_approve'})

    def create_payment_instruction(self, vbg_line):
        invoice_id = vbg_line.invoice_id if vbg_line.invoice_id else False
        agreement_id = vbg_line.agreement_id if vbg_line.agreement_id else False
        if invoice_id and agreement_id and round(invoice_id.residual, 2) > round(invoice_id.total_payment_amount, 2):
            payment_values = self.get_payment_instruction_values(invoice_id, agreement_id)

            pi = self.env['payment.instruction'].create(payment_values)
            vbg_line.write({'payment_instruction_id': pi.id})

        return True

    def get_payment_instruction_values(self, invoice_id, agreement_id):
        debit_acc = invoice_id.partner_id.property_account_payable_id.id
        op_unit = self.env['operating.unit'].search([('code', '=', '001')], limit=1)
        debit_branch = op_unit.id or False
        if invoice_id.partner_id.property_account_payable_sou_id:
            debit_sou = invoice_id.partner_id.property_account_payable_sou_id.id
        else:
            raise ValidationError("[Configuration Error]Please configure sequence for the following Vendor in account "
                                  "configuration: {}".format(invoice_id.partner_id.name))
        if agreement_id.payment_type == 'casa':
            vendor_bank_acc = agreement_id.vendor_bank_acc
            credit_acc = False
            credit_branch = False
            credit_sou = False

        elif agreement_id.payment_type == 'credit':
            vendor_bank_acc = False
            credit_acc = agreement_id.credit_account_id.id
            credit_branch = agreement_id.credit_operating_unit_id.id
            credit_sou = agreement_id.credit_sub_operating_unit_id.id if agreement_id.credit_sub_operating_unit_id else None

        if invoice_id.id:
            # generate reconcile ref code (Vendor Bills)
            reconcile_ref = invoice_id.get_reconcile_ref(debit_acc, invoice_id.id)

        payment_values = {
            'invoice_id': invoice_id.id or False,
            'advance_id': False,
            'security_return_id': False,
            'instruction_date': fields.Date.context_today(self),
            'amount': invoice_id.residual - invoice_id.total_payment_amount,
            'currency_id': invoice_id.currency_id.id,
            'default_debit_account_id': debit_acc,
            'debit_operating_unit_id': debit_branch,
            'debit_sub_operating_unit_id': debit_sou,
            'partner_id': invoice_id.partner_id.id,
            'vendor_bank_acc': vendor_bank_acc,
            'default_credit_account_id': credit_acc,
            'credit_operating_unit_id': credit_branch,
            'credit_sub_operating_unit_id': credit_sou,
            'narration': invoice_id.invoice_line_ids[0].name,
            'reconcile_ref': reconcile_ref
        }
        return payment_values


class VendorBillGenerationBillLine(models.Model):
    _inherit = 'vendor.bill.generation.line'

    payment_instruction_id = fields.Many2one('payment.instruction', string='Payment Instruction')
    payment_instruction_state = fields.Selection([('draft', "Waiting for Approval"),
                                                  ('approved', "Approved"),
                                                  ('cancel', "Cancel")], related='payment_instruction_id.state',
                                                 string='Payment Status')



