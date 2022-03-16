from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class VendorBillGeneration(models.Model):
    _name = 'vendor.bill.generation'
    _inherit = ['mail.thread']
    _description = 'Rent Bill Generation'
    _order = 'id desc'

    name = fields.Char('Name', required=False, track_visibility='onchange', default='/')
    narration = fields.Char('Narration', readonly=True, states={'draft': [('readonly', False)]})
    billing_period = fields.Selection([
        ('monthly', "Monthly"),
        ('yearly', "Yearly")], string="Billing Period", required=True,
        track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    billing_date = fields.Date('Billing Date', readonly=True, states={'draft': [('readonly', False)]},
                               default=lambda self: self.env.user.company_id.batch_date)
    period_id = fields.Many2one('date.range', string='Period', track_visibility='onchange', required=True,
                                readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', "Pending"),
        ('confirm', "Confirmed"),
        ('approve', "Approved"),
        ('bill_generate', "Bill Generated"),
        ('bill_validate', "Bill Validated"),
        ('cancel', "Canceled")], default='draft', string="Status",
        track_visibility='onchange')
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')
    line_ids = fields.One2many('vendor.bill.generation.line', 'vbg_id', string="Agreements", copy=True, auto_join=True,
                               readonly=True, states={'draft': [('readonly', False)]})
    bill_validate_button_visible = fields.Boolean('Bill Validation Button Visible', default=False)
    period_id_domain_ids = fields.Many2many('date.range', compute="compute_period_id_domain_ids", readonly=True,
                                            store=False)
    amount_total = fields.Float(string="Total Amount", compute="computer_rent_bill_values")
    amount_tds = fields.Float(string="TDS Payable", compute="computer_rent_bill_values")
    amount_vat_payable = fields.Float(string="VAT Payable", compute="computer_rent_bill_values")

    def computer_rent_bill_values(self):
        for rec in self:
            rec.amount_total = sum([line.invoice_id.amount_total for line in rec.line_ids if line.invoice_id])
            rec.amount_tds = sum([line.invoice_id.amount_tds for line in rec.line_ids if line.invoice_id])
            rec.amount_vat_payable = sum(
                [line.invoice_id.amount_vat_payable for line in rec.line_ids if line.invoice_id])

    @api.onchange('billing_period')
    def _onchange_billing_period(self):
        for rec in self:
            rec.period_id = None

    @api.onchange('period_id')
    def _onchange_period_id(self):
        for rec in self:
            rec.line_ids = None

    @api.depends('billing_period')
    def compute_period_id_domain_ids(self):
        date_range_env = self.env['date.range'].search([])
        for rec in self:
            if rec.billing_period == 'monthly':
                rec.period_id_domain_ids = date_range_env.filtered(lambda x: x.type_id.fiscal_month == True)
            elif rec.billing_period == 'yearly':
                rec.period_id_domain_ids = date_range_env.filtered(lambda x: x.type_id.fiscal_year == True)

    @api.multi
    def action_confirm(self):
        for rec in self:
            if rec.state == 'draft':
                if not rec.line_ids:
                    raise ValidationError('Please select agreement(s)')
                name = self.env['ir.sequence'].sudo().next_by_code('vendor.bill.generation') or ''
                rec.write({
                    'state': 'confirm',
                    'name': name,
                    'maker_id': self.env.user.id
                })

    @api.multi
    def action_approve(self):
        for rec in self:
            if rec.state == 'confirm':
                # if self.env.user.id == rec.maker_id.id and self.env.user.id != SUPERUSER_ID:
                #     raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
                rec.write({
                    'state': 'approve'
                })
                rec.action_bill_generate()
                for line in rec.line_ids:
                    line.write({'state': 'approve'})

    @api.multi
    def action_bill_generate(self):
        for rec in self:
            for line in rec.line_ids:
                agreement = line.agreement_id
                journal = self.env['account.journal'].search([('code', '=', 'VB')], limit=1)
                journal_id = journal.id
                billing_date = self.billing_date if self.billing_date else fields.date.today()
                invoice = self.create_simple_invoice(agreement, journal_id, billing_date, rec)
                line.write({'invoice_id': invoice.id})
            rec.write({'state': 'bill_generate',
                       'bill_validate_button_visible': True,
                       'maker_id': self.env.user.id})
        return True

    @api.multi
    def action_bill_validate(self):
        for rec in self:
            if rec.state == 'bill_generate':
                if self.env.user.id == rec.maker_id.id and self.env.user.id != SUPERUSER_ID:
                    raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
                invoice_ids = self.env['account.invoice'].search([('vbg_batch_id', '=', rec.id)])
                if invoice_ids:
                    for invoice in invoice_ids:
                        if invoice.state == 'draft':
                            invoice.action_invoice_open()
                rec.write({'state': 'bill_validate',
                           'bill_validate_button_visible': False,
                           'approver_id': self.env.user.id})

    def create_simple_invoice(self, agreement, journal_id, billing_date, rec):
        adjustment_value = agreement.adjustment_value if agreement.outstanding_amount >= agreement.adjustment_value \
            else agreement.outstanding_amount
        invoice = self.env['account.invoice'].create({
            'partner_id': agreement.partner_id.id,
            'account_id': agreement.partner_id.property_account_payable_id.id,
            'type': 'in_invoice',
            'journal_id': journal_id,
            'date_invoice': billing_date,
            'state': 'draft',
            'advance_ids': [(6, 0, [agreement.id])],
            'adjusted_advance': adjustment_value,
            'vbg_batch_id': rec.id
        })
        tax_ids = []
        if agreement.vat_id:
            tax_ids.append(agreement.vat_id.id)
        if agreement.tds_id:
            tax_ids.append(agreement.tds_id.id)

        self.env['account.invoice.line'].create({
            'product_id': agreement.product_id.id,
            'quantity': 1.0,
            'price_unit': agreement.total_service_value,
            'invoice_id': invoice.id,
            'name': rec.narration or agreement.product_id.name,
            'account_id': agreement.product_id.property_account_expense_id.id,
            'operating_unit_id': agreement.operating_unit_id.id,
            'sub_operating_unit_id': agreement.product_id.sub_operating_unit_id.id,
            'account_analytic_id': agreement.account_analytic_id.id,
            'vat_id': agreement.vat_id.id,
            'tds_id': agreement.tds_id.id,
            'invoice_line_tax_ids': [(4, val) for val in tax_ids]
        })
        tax_lines = invoice.get_taxes_values()
        invoice.write({'tax_line_ids': [(0, 0, tax_lines[val]) for val in tax_lines]})
        return invoice

    @api.multi
    def action_cancel(self):
        for rec in self:
            if rec.state == 'confirm':
                rec.write({
                    'state': 'cancel'
                })
                for line in rec.line_ids:
                    line.write({'state': 'cancel'})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not draft state!'))
        return super(VendorBillGeneration, self).unlink()


class VendorBillGenerationBillLine(models.Model):
    _name = 'vendor.bill.generation.line'

    vbg_id = fields.Many2one('vendor.bill.generation', string='Vendor Bill Generation ID',
                             ondelete='cascade', index=True, copy=False, required=True, readonly=True)
    agreement_id = fields.Many2one('vendor.advance', string='Agreement', required=True, readonly=True)
    description = fields.Char(string="Premise", related='agreement_id.description')
    period_id = fields.Many2one('date.range', string='Period', track_visibility='onchange', required=True,
                                readonly=True)
    invoice_id = fields.Many2one('account.invoice', string="Bill", readonly=True)
    bill_status = fields.Selection([
        ('draft', "Waiting for Approval"),
        ('proforma', "Pro-forma"),
        ('proforma2', "Pro-forma"),
        ('open', "Approved"),
        ('paid', "Paid"),
        ('cancel', "Cancelled")], string='Bill Status', related='invoice_id.state')
    state = fields.Selection([
        ('draft', "Pending"),
        ('approve', "Approved"),
        ('cancel', "Canceled")], default='draft', readonly=True)
    move_id = fields.Many2one('account.move', related='invoice_id.move_id', string='Journal')
