# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    _name = "purchase.order.line"

    invoice_id = fields.Many2one('account.invoice', string="SO Invoice", help="Invoices based on selected sale orders in customer claim!")


class InheritedPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    READONLY_STATES = {
        "sent": [('readonly', True)],
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    is_claim = fields.Boolean(string='C/R Claimed', help="Commission or Refund Claim Flag.", default=lambda self: self.env.context.get('is_claim') or False)
    sale_order_ids = fields.Many2many(
        comodel_name='sale.order',
        relation="purchase_order_commission_sale_order_rel",
        column1="purchase_order_commission_claim_id",
        column2="sale_order_id",
        string='Sale Order',
        states=READONLY_STATES
    )

    commission_claim_approve_uid = fields.Many2one('res.users', 'Approved By')

    def _get_operating_unit(self):
        domain = [("id", "in", self.env.user.operating_unit_ids.ids)]
        return domain

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit',
        states=READONLY_STATES,
        default=lambda self: (self.env['res.users'].operating_unit_default_get(self.env.uid)),
        domain=_get_operating_unit
    )

    @api.onchange('sale_order_ids')
    def _onchange_sale_order_ids(self):
        for rec in self:
            purchase_lines = [(5, 0, 0)]
            commission_control_acc = self.env['commission.refund.journal.config'].sudo().search([('company_id', '=', self.env.user.company_id.id)], limit=1)
            # making purchase order line based on selected SO
            for so in rec.sale_order_ids:
                for inv in so.invoice_ids:
                    for inv_line in inv.invoice_line_ids:
                        if inv_line.product_id:
                            commission_amount = inv_line.sale_line_ids.filtered(lambda r: r.product_id.id == inv_line.product_id.id).corporate_commission_per_unit
                            vals = {
                                "name": "Claim/" + self.name,
                                "date_planned": datetime.now().date(),
                                "currency_id": self.partner_id.property_purchase_currency_id.id,
                                "invoice_id": inv.id,
                                'company_id': so.company_id.id,
                                "product_id": inv_line.product_id.id,
                                "product_uom": inv_line.product_id.uom_id.id,
                                "product_qty": inv_line.quantity,
                                "price_unit": commission_amount,
                                "state": 'draft',
                            }
                            purchase_lines.append((0, 0, vals))

            rec.order_line = purchase_lines

    @api.model
    def create(self, vals):
        res = super(InheritedPurchaseOrder, self).create(vals)
        if res.id and vals.get('is_claim'):
            operating_unit_id = self.env['operating.unit'].browse(vals['operating_unit_id'])
            rec_name = self.env['ir.sequence'].next_by_code_new(
                'commission.claim', datetime.today(), operating_unit_id
            ) or '/'
            res.name = rec_name
           # res._onchange_sale_order_ids()

        return res

    # @api.multi
    # def button_draft_commission_claim(self):
    #     self.state = "draft"
    #     self.date_approve = False
    #     self.commission_claim_approve_uid = False
    #
    # @api.multi
    # def button_confirm_commission_claim(self):
    #     self.state = 'sent'
    #
    # @api.multi
    # def button_cancel_commission_claim(self):
    #     self.state = 'cancel'
    #
    # @api.multi
    # def button_approve_commission_claim(self):
    #     self.state = "purchase"
    #     self.commission_claim_approve_uid = self.env.user.id
    #     self.date_approve = datetime.today()
    #
    # @api.multi
    # def button_account_approve_commission_claim(self):
    #     self.state = "done"
    #     self.commission_claim_approve_uid = self.env.user.id
    #     self.date_approve = datetime.today()

    @api.multi
    def print_service_order(self):
        data = {'active_id': self.id}
        return self.env['report'].get_action(self, 'gbs_samuda_service_order.report_service_order', data)

    @api.multi
    @api.constrains('order_line')
    def _check_exist_product_in_line(self):
        if not self.is_claim:
            for purchase in self:
                exist_product_list = []
                for line in purchase.order_line:
                    if line.product_id.id in exist_product_list:
                        raise ValidationError(_('Product should be one per line.'))
                    exist_product_list.append(line.product_id.id)

    @api.multi
    def action_view_invoice(self):
        result = super(InheritedPurchaseOrder, self).action_view_invoice()
        if self.is_claim:
            result['context']['default_account_id'] = self.partner_id.commission_refund_account_payable_id.id
        return result
