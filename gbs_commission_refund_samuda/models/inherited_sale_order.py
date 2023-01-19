from collections import defaultdict
import json

# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from lxml import etree


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    commission_available = fields.Boolean(compute="_all_invoice_commission_available")
    refund_available = fields.Boolean(compute="_all_invoice_refund_available")

    @api.depends("commission_available")
    def _all_invoice_commission_available(self):
        for rec in self:
            is_claim_cancelled = self.env['purchase.order'].sudo().search([('sale_order_ids', 'in', [rec.id])], limit=1, order="id desc")
            if is_claim_cancelled.state == 'cancel':
                rec.commission_available = True
            else:
                # any(list) returns True if any item in an iterable are true, otherwise it returns False
                available = any([(not inv.is_commission_claimed and (inv.state == 'paid' or inv.state == 'open') and inv.type == 'out_invoice') for inv in rec.invoice_ids])

                total_commission = 0
                for inv in rec.invoice_ids:
                    for inv_line in inv.invoice_line_ids:
                        total_commission += sum([line.corporate_commission_per_unit for line in inv_line.sale_line_ids])

                rec.commission_available = total_commission > 0 and available

    @api.depends("refund_available")
    def _all_invoice_refund_available(self):
        for rec in self:
            is_claim_cancelled = self.env['purchase.order'].sudo().search([('sale_order_ids', 'in', [rec.id])], limit=1, order="id desc")
            if is_claim_cancelled.state == 'cancel':
                rec.refund_available = True
            else:
                # any(list) returns True if any item in an iterable are true, otherwise it returns False
                available = any([(not inv.is_refund_claimed and (inv.state == 'paid' or inv.state == 'open') and inv.type == 'out_invoice') for inv in rec.invoice_ids])

                total_commission = 0
                for inv in rec.invoice_ids:
                    for inv_line in inv.invoice_line_ids:
                        total_commission += sum([line.corporate_refund_per_unit for line in inv_line.sale_line_ids])

                rec.refund_available = total_commission > 0 and available
