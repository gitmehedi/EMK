from collections import defaultdict

# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    commission_available = fields.Boolean(compute="_all_invoice_commission_available")
    refund_available = fields.Boolean(compute="_all_invoice_refund_available")

    @api.depends("commission_available")
    def _all_invoice_commission_available(self):
        for rec in self:
            # any(list) returns True if any item in an iterable are true, otherwise it returns False
            available = any([not inv.is_commission_claimed and inv.state == 'paid' for inv in rec.invoice_ids])

            total_commission = 0
            for inv in rec.invoice_ids:
                for inv_line in inv.invoice_line_ids:
                    total_commission += sum([line.corporate_commission_per_unit for line in inv_line.sale_line_ids])

            rec.commission_available = total_commission > 0 and available

    @api.depends("refund_available")
    def _all_invoice_refund_available(self):
        for rec in self:
            # any(list) returns True if any item in an iterable are true, otherwise it returns False
            available = any([not inv.is_refund_claimed and inv.state == 'paid' for inv in rec.invoice_ids])

            total_commission = 0
            for inv in rec.invoice_ids:
                for inv_line in inv.invoice_line_ids:
                    total_commission += sum([line.corporate_refund_per_unit for line in inv_line.sale_line_ids])

            rec.refund_available = total_commission > 0 and available


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    corporate_commission_per_unit = fields.Float(string="Commission Per Unit")
    corporate_commission_tolerable = fields.Float(string="Commission Tolerable")
    corporate_refund_per_unit = fields.Float(digits=(16, 2), string="Refund Per Unit")
    corporate_refund_tolerable = fields.Float(string="Refund Tolerable")

    dealer_commission_applicable = fields.Boolean(string='Commission Applicable')
    dealer_refund_applicable = fields.Boolean(string='Refund Applicable')

    @api.onchange('product_id', 'product_uom')
    def _onchange_commission_refund_product_id(self):
        for rec in self:
            rec.corporate_commission_per_unit = 0.0
            rec.corporate_commission_tolerable = 0.0
            rec.corporate_refund_per_unit = 0.0
            rec.corporate_refund_tolerable = 0.0
            rec.dealer_commission_applicable = False
            rec.dealer_refund_applicable = False

            if rec.product_id:
                product_package_mode = rec.order_id.pack_type.id
                uom_id = rec.product_uom.id or rec.product_id.uom_id.id
                pricelist_id = self.env['product.sales.pricelist'].sudo().search(
                    [('product_id', '=', rec.product_id.id), ('uom_id', '=', uom_id), ('product_package_mode', '=', product_package_mode)],
                    limit=1
                )

                if pricelist_id:
                    rec.corporate_commission_per_unit = pricelist_id.corporate_commission_per_unit
                    rec.corporate_commission_tolerable = pricelist_id.corporate_commission_tolerable
                    rec.corporate_refund_per_unit = pricelist_id.corporate_refund_per_unit
                    rec.corporate_refund_tolerable = pricelist_id.corporate_refund_tolerable
                    rec.dealer_commission_applicable = pricelist_id.dealer_commission_applicable
                    rec.dealer_refund_applicable = pricelist_id.dealer_refund_applicable
