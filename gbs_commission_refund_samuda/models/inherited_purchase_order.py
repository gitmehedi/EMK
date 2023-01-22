# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from lxml import etree


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    invoice_id = fields.Many2one(
        'account.invoice',
        string="SO Invoice",
        help="Invoices based on selected sale orders in customer claim!"
    )


class InheritedPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    READONLY_STATES = {
        "claim_hos_approve": [('readonly', True)],
        'claim_hoa_approve': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    def _sale_order_domain(self):
        return [('partner_id', '=', self.partner_id.id), ('operating_unit_id', '=', self.operating_unit_id.id)]

    def _get_operating_unit(self):
        domain = [("id", "in", self.env.user.operating_unit_ids.ids)]
        return domain

    is_commission_claim = fields.Boolean(
        string='Commission',
        help="Commission Claim Flag.",
        default=lambda self: self.env.context.get('is_commission_claim') or False
    )
    is_refund_claim = fields.Boolean(
        string='Refund',
        help="Refund Claim Flag.",
        default=lambda self: self.env.context.get('is_refund_claim') or False
    )
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('claim_draft', 'New'),
        ('claim_hos_approve', 'Sales Approval'),
        ('claim_hoa_approve', 'Accounts Approval'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    sale_order_ids = fields.Many2many(
        comodel_name='sale.order',
        relation="purchase_order_commission_sale_order_rel",
        column1="purchase_order_commission_claim_id",
        column2="sale_order_id",
        string='Sale Order',
        states=READONLY_STATES,
        domain=_sale_order_domain,
    )
    commission_claim_approve_uid = fields.Many2one('res.users', 'Approved By')
    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit',
        states=READONLY_STATES,
        default=lambda self: (self.env['res.users'].operating_unit_default_get(self.env.uid)),
        domain=_get_operating_unit
    )

    @api.onchange('partner_id', 'operating_unit_id')
    def _onchange_sale_order_domain(self):
        if self.partner_id:
            self.region_type = self.partner_id.supplier_type

        # clear existing records
        self.sale_order_ids = [(5, 0, 0)]
        self.order_line = [(5, 0, 0)]

        if self.partner_id and self.operating_unit_id:
            # sale_order_ids = self.env['sale.order'].sudo().search([('partner_id', '=', self.partner_id.id), ('operating_unit_id', '=', self.operating_unit_id.id)])
            sale_order_ids = self.env['sale.order'].sudo().search([('partner_id', '=', self.partner_id.id)])
            available_ids = []
            for sale_order in sale_order_ids:
                if self.is_commission_claim:
                    if sale_order.commission_available:
                        available_ids.append(sale_order.id)
                else:
                    if sale_order.refund_available:
                        available_ids.append(sale_order.id)

            return {'domain': {'sale_order_ids': [('id', 'in', available_ids)]}}

    @api.onchange('sale_order_ids')
    def _onchange_sale_order_ids(self):
        for rec in self:
            purchase_lines = [(5, 0, 0)]

            # making purchase order line based on selected SO
            for so in rec.sale_order_ids:
                for inv in so.invoice_ids:

                    if inv.type != 'out_invoice' or not (inv.state == 'paid' or inv.state == 'open'):
                        continue  # skip if not out invoice or state is not in paid or open state.

                    # if there already added this invoice to purchase order line for current purchase order then keep it.
                    temp_invoice_ids = self.env['purchase.order.line'].search([('invoice_id', '=', inv.id)])

                    if self.is_commission_claim and inv.is_commission_claimed and not temp_invoice_ids:
                        continue
                    elif self.is_refund_claim and inv.is_refund_claimed and not temp_invoice_ids:
                        continue

                    for inv_line in inv.invoice_line_ids:
                        if inv_line.product_id and inv_line.quantity > 0:
                            temp_product_id = inv_line.sale_line_ids.filtered(lambda r: r.product_id.id == inv_line.product_id.id)
                            commission_amount = temp_product_id.corporate_commission_per_unit if self.is_commission_claim else temp_product_id.corporate_refund_per_unit
                            if commission_amount <= 0:
                                continue  # skip invoice if commission/refund balance is zero or less.

                            qty = inv_line.quantity

                            if (self.is_commission_claim and so.deduct_commission) or (self.is_refund_claim and so.deduct_refund):
                                # get all the invoice that is used the reference of current inv number
                                invoice_lines_1 = self.env['account.invoice'].sudo().search([
                                    ('from_return', '=', True), ('refund_invoice_id', '=', inv.id), ('type', '=', 'out_refund')]
                                )
                                for return_inv_line in invoice_lines_1:
                                    for inv_line_1 in return_inv_line.invoice_line_ids:
                                        qty -= sum([inv_1.quantity for inv_1 in inv_line_1])

                            vals = {
                                "name": inv_line.product_id.name,
                                "date_planned": datetime.now().date(),
                                "currency_id": self.partner_id.property_purchase_currency_id.id,
                                "invoice_id": inv.id,
                                'company_id': so.company_id.id,
                                "product_id": inv_line.product_id.id,
                                "product_uom": inv_line.product_id.uom_id.id,
                                "product_qty": qty,
                                "price_unit": commission_amount,
                                "state": 'draft',
                            }
                            purchase_lines.append((0, 0, vals))

            rec.order_line = purchase_lines

    @api.model
    def create(self, vals):
        res = super(InheritedPurchaseOrder, self).create(vals)
        if res.id and (vals.get('is_commission_claim') or vals.get('is_refund_claim')):
            operating_unit_id = self.env['operating.unit'].browse(vals['operating_unit_id'])
            seq = 'commission.claim' if vals.get('is_commission_claim') else 'refund.claim'
            rec_name = self.env['ir.sequence'].next_by_code_new(seq, datetime.today(), operating_unit_id) or '/'
            res.name = rec_name
            res.state = 'claim_draft'

        return res

    @api.multi
    @api.constrains('order_line')
    def _check_exist_product_in_line(self):
        if not (self.is_commission_claim or self.is_refund_claim):
            super(InheritedPurchaseOrder, self)._check_exist_product_in_line()

    @api.multi
    def action_view_invoice(self):
        result = super(InheritedPurchaseOrder, self).action_view_invoice()
        if self.is_commission_claim or self.is_refund_claim:
            result['context']['default_account_id'] = self.partner_id.commission_refund_account_payable_id.id
            result['context']['default_is_claimed'] = True
            # result['context']['no_create_edit_button'] = True
        else:
            result['context']['default_account_id'] = self.partner_id.property_account_payable_id.id
        return result

    @api.multi
    def button_claim_confirm(self):
        self.state = 'claim_hos_approve'

    @api.multi
    def button_claim_validate(self):
        self.state = 'claim_hoa_approve'

    @api.multi
    def button_claim_approve(self):
        self.state = 'done'
        self.commission_claim_approve_uid = self.env.user.id
        self.date_approve = fields.Date.today()

    @api.multi
    def button_draft(self):
        super(InheritedPurchaseOrder, self).button_draft()
        if self.is_commission_claim or self.is_refund_claim:
            self.state = "claim_draft"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(InheritedPurchaseOrder, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                                  toolbar=toolbar,
                                                                  submenu=submenu)

        doc = etree.XML(res['arch'])
        no_create_edit_button = self.env.context.get('no_create_edit_button')
        if no_create_edit_button:
            if view_type == 'form' or view_type == 'kanban' or view_type == 'tree':
                for node_form in doc.xpath("//kanban"):
                    node_form.set("create", 'false')
                for node_form in doc.xpath("//tree"):
                    node_form.set("create", 'false')
                for node_form in doc.xpath("//form"):
                    node_form.set("create", 'false')

        res['arch'] = etree.tostring(doc)
        return res
