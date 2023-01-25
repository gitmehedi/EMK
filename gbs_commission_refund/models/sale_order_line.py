from collections import defaultdict
import json

# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

from lxml import etree


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    deduct_commission = fields.Boolean(
        string='Deduct Commission on Return',
        help='We will deduct the amount of returned quantity from actual invoiced quantity'
    )
    deduct_refund = fields.Boolean(
        string='Deduct Refund on Return',
        help='We will deduct the amount of returned quantity from actual invoiced quantity'
    )

    @api.onchange('pack_type', 'order_line')
    def _onchange_pack_type_order_line(self):
        for rec in self:
            for so in rec.order_line:
                so._onchange_commission_refund_product_id()

    @api.multi
    def check_second_approval(self, line, price_change_pool, causes):
        self.ensure_one()
        is_double_validation = False

        res = super(SaleOrder, self).check_second_approval(line, price_change_pool, causes)

        commission_tolerable_min = (line.commission_actual - line.commission_tolerable)
        commission_tolerable_max = (line.commission_actual + line.commission_tolerable)

        if line.corporate_commission_per_unit < commission_tolerable_min or line.corporate_commission_per_unit > commission_tolerable_max:
            actual_commission_msg = "no approved commission available."

            if commission_tolerable_max > 0:
                commission_range = "{}".format(line.commission_actual)
                if line.commission_tolerable > 0:
                    commission_range = "between {} to {}".format(commission_tolerable_min, commission_tolerable_max)
                actual_commission_msg = "approved commission is {}".format(commission_range)

            temp_msg = "Requested Commission rate is {} but {}".format(
                line.corporate_commission_per_unit,
                actual_commission_msg
            )
            causes.append(temp_msg)
            is_double_validation = True

        refund_tolerable_min = (line.refund_actual - line.refund_tolerable)
        refund_tolerable_max = (line.refund_actual + line.refund_tolerable)

        if line.corporate_refund_per_unit < refund_tolerable_min or line.corporate_refund_per_unit > refund_tolerable_max:
            actual_refund_msg = "no approved refund available."

            if refund_tolerable_max > 0:
                refund_range = "{}".format(line.refund_actual)
                if line.refund_tolerable > 0:
                    refund_range = "between {} to {}".format(refund_tolerable_min, refund_tolerable_max)
                actual_refund_msg = "approved refund is {}".format(refund_range)

            temp_msg = "Requested Refund rate is {} but {}".format(line.corporate_refund_per_unit, actual_refund_msg)
            causes.append(temp_msg)
            is_double_validation = True

        return res or is_double_validation  # if any is true then double validation is required.

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(SaleOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                        submenu=submenu)

        commission_start_date = self.env['ir.values'].sudo().get_default('sale.config.settings', 'commission_start_date')

        if self.date_order:
            sale_order_date = self.date_order.date()
        else:
            sale_order_date = datetime.now().date()

        invisible_commission_fields = True
        if commission_start_date:
            commission_start_date = datetime.strptime(commission_start_date, "%Y-%m-%d").date()
            if sale_order_date > commission_start_date:
                invisible_commission_fields = False
        else:
            raise UserError('Commission/Refund feature start date not found in configuration!')

        if view_type == 'form':
            company = self.env.user.company_id
            config = self.env['commission.configuration'].search([
                ('process', '=', 'textbox'),
                ('customer_type', 'in', company.customer_types.ids or []),
                ('functional_unit', 'in', company.branch_ids.ids or [])
            ], limit=1)

            order_line_tree = etree.XML(result['fields']['order_line']['views']['tree']['arch'])

            # hide tax column when show tax is False.
            if not config.show_tax:
                for field in order_line_tree.xpath("//field[@name='tax_id']"):
                    modifiers = json.loads(field.get('modifiers', '{}'))
                    modifiers['invisible'] = True
                    modifiers['tree_invisible'] = True
                    modifiers['column_invisible'] = True
                    field.set('modifiers', json.dumps(modifiers))

            if invisible_commission_fields or config.process != 'textbox':
                fields_to_be_hidden = ['corporate_commission_per_unit', 'corporate_refund_per_unit']
                for f in fields_to_be_hidden:
                    for field in order_line_tree.xpath("//field[@name='%s']" % f):
                        modifiers = json.loads(field.get('modifiers', '{}'))
                        modifiers['invisible'] = True
                        modifiers['tree_invisible'] = True
                        modifiers['column_invisible'] = True
                        field.set('modifiers', json.dumps(modifiers))

            if invisible_commission_fields or config.process != 'checkbox':
                fields_to_be_hidden = ['dealer_commission_applicable', 'dealer_refund_applicable']
                for f in fields_to_be_hidden:
                    for field in order_line_tree.xpath("//field[@name='%s']" % f):
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

    @api.multi
    def action_reset(self):
        self.comment = False
        super(SaleOrder, self).action_reset()

    @api.multi
    def action_to_submit(self):
        is_double_validation = False
        causes = []

        for order in self:
            partner_pool = order.partner_id
            for lines in order.order_line:
                price_change_pool = order.env['product.sale.history.line'].search(
                    [('product_id', '=', lines.product_id.id),
                     ('currency_id', '=', lines.currency_id.id),
                     ('product_package_mode', '=', order.pack_type.id),
                     ('uom_id', '=', lines.product_uom.id)], limit=1)

                is_double_validation = order.check_second_approval(lines, price_change_pool, causes)

            if order.credit_sales_or_lc == 'credit_sales':
                returned_list = self.get_customer_credit_limit(partner_pool, order)

                if abs(returned_list[0]) > returned_list[1]:
                    causes.append(
                        "Customer crossed his Credit Limit. Current Credit Limit is " + str(abs(returned_list[1])))
                    is_double_validation = True

            if is_double_validation:
                comment_str = "Acceptance needs for " + str(len(causes)) + " cause(s) which are: <br/>"
                comment_str += "<br/>".join(causes)
                order.sudo().write({'comment': comment_str})  # Go to two level approval process

        return super(SaleOrder, self).action_to_submit()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_unit_copy = fields.Float(string='Price_unit_copy')
    price_unit_actual = fields.Float(string='Price Unit Actual')
    price_unit_max_discount = fields.Float(string="Max Discount Amount")

    corporate_commission_per_unit = fields.Float(string="Commission Per Unit")
    commission_per_unit_copy = fields.Float(string="Commission Per Unit Copy")

    commission_actual = fields.Float(string="Commission Actual")
    commission_tolerable = fields.Float(string="Commission Tolerable")

    corporate_refund_per_unit = fields.Float(digits=(16, 2), string="Refund Per Unit")
    refund_per_unit_copy = fields.Float(digits=(16, 2), string="Refund Per Unit Copy")

    refund_actual = fields.Float(string="Refund Actual")
    refund_tolerable = fields.Float(string="Refund Tolerable")

    dealer_commission_applicable = fields.Boolean(string='Commission Applicable')
    commission_applicable_copy = fields.Boolean(string='Commission Applicable Copy')

    dealer_refund_applicable = fields.Boolean(string='Refund Applicable')
    refund_applicable_copy = fields.Boolean(string='Refund Applicable Copy')

    so_readonly_field = fields.Boolean(compute="_compute_so_readonly_field")

    @api.one
    @api.constrains('corporate_commission_per_unit', 'corporate_refund_per_unit')
    def _textbox_process_validation(self):
        commission_start_date = self.env['ir.values'].sudo().get_default('sale.config.settings', 'commission_start_date')

        if self.order_id.date_order:
            sale_order_date = self.order_id.date_order
        else:
            sale_order_date = datetime.now().date()

        if commission_start_date:
            if sale_order_date < commission_start_date and (self.corporate_commission_per_unit > 0 or self.corporate_refund_per_unit > 0):
                raise UserError('Commission/Refund feature not applicable before dated %s' % commission_start_date)
        else:
            raise UserError('Commission/Refund feature start date not found in configuration!')

    @api.one
    @api.constrains('dealer_commission_applicable', 'dealer_refund_applicable')
    def _checkbox_process_validation(self):
        commission_start_date = self.env['ir.values'].sudo().get_default('sale.config.settings', 'commission_start_date')

        if self.order_id.date_order:
            sale_order_date = self.order_id.date_order
        else:
            sale_order_date = datetime.now().date()

        if commission_start_date:
            if sale_order_date < commission_start_date and (self.dealer_commission_applicable or self.dealer_refund_applicable):
                raise UserError('Commission/Refund feature not applicable before dated %s' % commission_start_date)
        else:
            raise UserError('Commission/Refund feature start date not found in configuration!')

    @api.onchange('product_id', 'product_uom')
    def _onchange_commission_refund_product_id(self):
        self._compute_so_readonly_field()
        company_id = self.env.user.company_id

        domain = [
            ('process', '=', 'textbox'),
            ('customer_type', 'in', company_id.customer_types.ids or []),
            ('functional_unit', 'in', company_id.branch_ids.ids or [])
        ]
        config = self.env['commission.configuration'].sudo().search(domain, limit=1)

        for rec in self:
            rec.price_unit_actual = 0
            rec.price_unit_max_discount = 0

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
                pricelist_id = self.env['product.sale.history.line'].search([
                    ('product_id', '=', rec.product_id.id),
                    ('currency_id', '=', rec.order_id.currency_id.id),
                    ('product_package_mode', '=', product_package_mode),
                    ('uom_id', '=', uom_id)
                ], limit=1)

                if pricelist_id:
                    rec.price_unit_actual = pricelist_id.new_price
                    rec.price_unit_max_discount = pricelist_id.discount

                    if config and config.auto_load_commission_refund_in_so_line:
                        rec.corporate_commission_per_unit = pricelist_id.corporate_commission_per_unit
                        rec.corporate_refund_per_unit = pricelist_id.corporate_refund_per_unit

                        rec.price_unit_copy = pricelist_id.new_price
                        rec.commission_per_unit_copy = pricelist_id.corporate_commission_per_unit
                        rec.refund_per_unit_copy = pricelist_id.corporate_refund_per_unit

                    # commission & refund applicable or not for dealer only.
                    rec.dealer_commission_applicable = pricelist_id.dealer_commission_applicable
                    rec.dealer_refund_applicable = pricelist_id.dealer_refund_applicable

                    rec.commission_applicable_copy = pricelist_id.dealer_commission_applicable
                    rec.refund_applicable_copy = pricelist_id.dealer_refund_applicable

                    # commission
                    rec.commission_actual = pricelist_id.corporate_commission_per_unit
                    rec.commission_tolerable = pricelist_id.corporate_commission_tolerable

                    # refund
                    rec.refund_actual = pricelist_id.corporate_refund_per_unit
                    rec.refund_tolerable = pricelist_id.corporate_refund_tolerable

    @api.depends("so_readonly_field")
    def _compute_so_readonly_field(self):
        company = self.env.user.company_id
        is_readonly = self.env['commission.configuration'].search([
            ('customer_type', 'in', company.customer_types.ids or []),
            ('functional_unit', 'in', company.branch_ids.ids or []),
        ], limit=1).so_readonly_field or False

        for rec in self:
            rec.so_readonly_field = is_readonly

    @api.onchange('price_unit')
    def _onchange_price_unit(self):
        self.price_unit_copy = self.price_unit

    @api.model
    def create(self, values):
        res = super(SaleOrderLine, self).create(values)
        company_id = self.env.user.company_id

        domain = [
            ('customer_type', 'in', company_id.customer_types.ids or []),
            ('functional_unit', 'in', company_id.branch_ids.ids or [])
        ]
        config = self.env['commission.configuration'].sudo().search(domain, limit=1)
        if config.so_readonly_field:
            if 'price_unit_copy' in values:
                res.price_unit = res.price_unit_copy
            if 'commission_per_unit_copy' in values:
                res.corporate_commission_per_unit = res.commission_per_unit_copy
            if 'refund_per_unit_copy' in values:
                res.corporate_refund_per_unit = res.refund_per_unit_copy
            if 'commission_applicable_copy' in values:
                res.dealer_commission_applicable = res.commission_per_unit_copy
            if 'refund_applicable_copy' in values:
                res.dealer_refund_applicable = res.refund_per_unit_copy

        return res

    @api.multi
    def write(self, values):
        if self.so_readonly_field:
            if 'price_unit_copy' in values:
                values['price_unit'] = values['price_unit_copy']
            if 'commission_per_unit_copy' in values:
                values['corporate_commission_per_unit'] = values['commission_per_unit_copy']
            if 'refund_per_unit_copy' in values:
                values['corporate_refund_per_unit'] = values['refund_per_unit_copy']
            if 'commission_applicable_copy' in values:
                values['dealer_commission_applicable'] = values['commission_applicable_copy']
            if 'refund_applicable_copy' in values:
                values['dealer_refund_applicable'] = values['refund_applicable_copy']

        return super(SaleOrderLine, self).write(values)

    @api.one
    @api.constrains('product_uom_qty', 'corporate_refund_per_unit', 'corporate_commission_per_unit')
    def _check_order_line_inputs(self):
        # super(SaleOrderLine, self)._check_order_line_inputs()
        if self.corporate_refund_per_unit or self.corporate_commission_per_unit:
            if self.corporate_refund_per_unit < 0 or self.corporate_commission_per_unit < 0:
                raise ValidationError('Commission, Refund amount can not be Negative value')
