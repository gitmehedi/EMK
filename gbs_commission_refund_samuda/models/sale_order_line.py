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

    @api.multi
    def check_second_approval(self, line, price_change_pool, causes):
        self.ensure_one()
        is_double_validation = False
        # product_id = line.product_id.id
        # uom_id = line.product_uom.id
        # product_package_mode = line.order_id.pack_type.id

        # pricelist_id = self.env['product.sales.pricelist'].sudo().search(
        #     [('product_id', '=', line.product_id.id), ('uom_id', '=', uom_id), ('product_package_mode', '=', product_package_mode)],
        #     limit=1
        # )

        if line.corporate_commission_per_unit > (line.commission_actual + line.commission_tolerable):
            causes.append("No commission found for `{}` but requested commission is = {}".format(line.product_id.name, line.corporate_commission_per_unit))
            is_double_validation = True

        if line.corporate_refund_per_unit > (line.refund_actual + line.refund_tolerable):
            causes.append("No refund found for `{}` but requested commission is = {}".format(line.product_id.name, line.corporate_commission_per_unit))
            is_double_validation = True

        res = super(SaleOrder, self).check_second_approval(line, price_change_pool, causes)
        return res or is_double_validation

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(SaleOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            company = self.env.user.company_id
            config = self.env['commission.configuration'].search([('customer_type', 'in', company.customer_types.ids or []), ('functional_unit', 'in', company.branch_ids.ids or [])], limit=1)

            # hide tax column when show tax is False.
            if not config.show_tax:
                order_line_tree = etree.XML(result['fields']['order_line']['views']['tree']['arch'])

                for field in order_line_tree.xpath("//field[@name='tax_id']"):
                    modifiers = json.loads(field.get('modifiers', '{}'))
                    modifiers['invisible'] = True
                    modifiers['tree_invisible'] = True
                    modifiers['column_invisible'] = True
                    field.set('modifiers', json.dumps(modifiers))

                result['fields']['order_line']['views']['tree']['arch'] = etree.tostring(order_line_tree)

            if not config.show_packing_mode:
                so_form = etree.XML(result['arch'])
                for field in so_form.xpath("//field[@name='pack_type']"):
                    modifiers = json.loads(field.get('modifiers', '{}'))
                    modifiers['invisible'] = True
                    modifiers['tree_invisible'] = True
                    modifiers['column_invisible'] = True
                    field.set('modifiers', json.dumps(modifiers))

                result['arch'] = etree.tostring(so_form)

        return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    corporate_commission_per_unit = fields.Float(string="Commission Per Unit")
    commission_actual = fields.Float(string="Commission Actual")
    commission_tolerable = fields.Float(string="Commission Tolerable")

    corporate_refund_per_unit = fields.Float(digits=(16, 2), string="Refund Per Unit")
    refund_actual = fields.Float(string="Refund Actual")
    refund_tolerable = fields.Float(string="Refund Tolerable")

    dealer_commission_applicable = fields.Boolean(string='Commission Applicable')
    dealer_refund_applicable = fields.Boolean(string='Refund Applicable')

    so_readonly_field = fields.Boolean(compute="_compute_so_readonly_field")

    @api.onchange('product_id', 'product_uom')
    def _onchange_commission_refund_product_id(self):
        self._compute_so_readonly_field()

        company_id = self.env.user.company_id

        domain = [('customer_type', 'in', company_id.customer_types.ids or []), ('functional_unit', 'in', company_id.branch_ids.ids or [])]
        config = self.env['commission.configuration'].sudo().search(domain, limit=1)

        if config and config.auto_load_commission_refund_in_so_line:
            for rec in self:
                rec.corporate_commission_per_unit = 0.0
                rec.commission_actual = 0.0
                rec.commission_tolerable = 0.0

                rec.corporate_refund_per_unit = 0.0
                rec.refund_actual = 0.0
                rec.refund_tolerable = 0.0

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
                        # commission
                        rec.corporate_commission_per_unit = pricelist_id.corporate_commission_per_unit
                        rec.commission_actual = pricelist_id.corporate_commission_per_unit
                        rec.commission_tolerable = pricelist_id.corporate_commission_tolerable

                        # refund
                        rec.corporate_refund_per_unit = pricelist_id.corporate_refund_per_unit
                        rec.refund_actual = pricelist_id.corporate_refund_per_unit
                        rec.refund_tolerable = pricelist_id.corporate_refund_tolerable

                        # commission & refund applicable or not for dealar only.
                        rec.dealer_commission_applicable = pricelist_id.dealer_commission_applicable
                        rec.dealer_refund_applicable = pricelist_id.dealer_refund_applicable

    @api.depends("so_readonly_field")
    def _compute_so_readonly_field(self):
        company = self.env.user.company_id
        is_readonly = self.env['commission.configuration'].search([
            ('customer_type', 'in', company.customer_types.ids or []),
            ('functional_unit', 'in', company.branch_ids.ids or []),
        ], limit=1).so_readonly_field or False

        for rec in self:
            rec.so_readonly_field = is_readonly
