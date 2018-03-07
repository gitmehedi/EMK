from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import amount_to_text_en
import time


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_order_type(self):
        return self.env['sale.order.type'].search([], limit=1)

    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()

    type_id = fields.Many2one(comodel_name='sale.order.type', string='Type', default=_get_order_type, readonly=True,
                              states={'to_submit': [('readonly', False)]})

    order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines', readonly=True, copy=True)
    incoterm = fields.Many2one('stock.incoterms', 'Incoterms', readonly=True,
                               help="International Commercial Terms are a series of predefined commercial terms used in international transactions.",
                               states={'to_submit': [('readonly', False)]})
    client_order_ref = fields.Char(string='Customer Reference', copy=False, readonly=True,
                                   states={'to_submit': [('readonly', False)]})
    team_id = fields.Many2one('crm.team', 'Sales Team', change_default=True, readonly=True, default=_get_default_team,
                              oldname='section_id', states={'to_submit': [('readonly', False)]})
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user, readonly=True,
                              states={'to_submit': [('readonly', False)]})
    fiscal_position_id = fields.Many2one('account.fiscal.position', oldname='fiscal_position', string='Fiscal Position',
                                         readonly=True, states={'to_submit': [('readonly', False)]})
    origin = fields.Char(string='Source Document',
                         help="Reference of the document that generated this sales order request.", readonly=True,
                         states={'to_submit': [('readonly', False)]})

    credit_sales_or_lc = fields.Selection([
        ('cash', 'Cash'),
        ('credit_sales', 'Credit'),
        ('lc_sales', 'L/C'),
    ], string='Sales Type', required=True)

    state = fields.Selection([
        ('to_submit', 'Submit'),
        ('draft', 'Quotation'),
        ('submit_quotation', 'Validate'),
        ('validate', 'Accounts Approval'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='to_submit')

    def _get_pack_type(self):
        return self.env['product.packaging.mode'].search([], limit=1)

    pack_type = fields.Many2one('product.packaging.mode', string='Packing Mode', default=_get_pack_type, required=True)
    currency_id = fields.Many2one("res.currency", related='', string="Currency", required=True)

    """ PI and LC """
    pi_no = fields.Many2one('proforma.invoice', string='PI Ref. No.')
    lc_no = fields.Many2one('letter.credit', string='LC Ref. No.')

    remaining_credit_limit = fields.Char(string="Customer's Remaining Credit Limit", track_visibility='onchange')

    """ Update is_commission_generated flag to False """

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        res = super(SaleOrder, self).action_invoice_create()

        # acc_inv_pool = self.env['account.invoice']
        self.invoice_ids.write({'is_commission_generated': False})

        return res

    @api.depends('order_line.da_qty')
    def _da_button_show_hide(self):
        for sale_orders in self:
            for sale_line in sale_orders.order_line:
                if sale_line.da_qty == 0.00:
                    sale_orders.da_btn_show_hide = True
                else:
                    sale_orders.da_btn_show_hide = False
                    break;

    da_btn_show_hide = fields.Boolean(string="Is DA btn visible", compute="_da_button_show_hide", store=True)

    @api.multi
    def amount_to_word(self, number):
        if self.currency_id.name.encode('ascii', 'ignore') == 'BDT':
            return self.env['res.currency'].amount_to_word(float(number))
        else:
            currency = self.currency_id.name.encode('ascii', 'ignore')
            return amount_to_text_en.amount_to_text(number, 'en', currency)

    @api.multi
    def action_validate(self):
        self.state = 'sent'

    @api.multi
    def action_to_submit(self):
        for orders in self:
            if orders.validity_date and orders.validity_date <= orders.date_order:
                raise UserError('Expiration Date can not be less than Order Date')

            orders.state = 'draft'

    @api.onchange('type_id')
    def onchange_type(self):
        sale_type_pool = self.env['sale.order.type'].search([('id', '=', self.type_id.id)])
        if self.type_id:
            self.credit_sales_or_lc = sale_type_pool.sale_order_type
            self.currency_id = sale_type_pool.currency_id.id

    @api.multi
    def _is_double_validation_applicable(self):
        for orders in self:
            if orders.credit_sales_or_lc == 'lc_sales':
                # If LC and PI ref is present, go to the Final Approval, Else go to Second level approval
                if orders.lc_no and orders.pi_no:
                    for lines in orders.order_line:
                        product_pool = orders.env['product.product'].search([('id', '=', lines.product_id.ids)])
                        if (lines.price_unit != product_pool.list_price):
                            return True  # Go to two level approval process

                    return False  # One level approval process
                elif orders.pi_no and not orders.lc_no:
                    return True  # Go to two level approval process
                else:
                    return False  # Go to two level approval process

            elif orders.credit_sales_or_lc == 'credit_sales':

                for lines in orders.order_line:

                    cust_commission_pool = orders.env['customer.commission'].search(
                        [('customer_id', '=', orders.partner_id.id), ('product_id', '=', lines.product_id.ids)])
                    credit_limit_pool = orders.env['res.partner'].search([('id', '=', orders.partner_id.id)])

                    price_change_pool = self.env['product.sale.history.line'].search(
                        [('product_id', '=', lines.product_id.id),
                         ('currency_id', '=', lines.currency_id.id),
                         ('product_package_mode', '=', orders.pack_type.id),
                         ('uom_id', '=', lines.product_uom.id)])

                    account_receivable = credit_limit_pool.credit
                    sales_order_amount_total = -orders.amount_total  # actually it should be minus value

                    customer_total_credit = account_receivable + sales_order_amount_total
                    customer_credit_limit = credit_limit_pool.credit_limit

                    if (abs(customer_total_credit) > customer_credit_limit
                        or lines.commission_rate != cust_commission_pool.commission_rate
                        or lines.price_unit != price_change_pool.new_price):

                        return True
                        break;
                    else:
                        return False

        for lines in self.order_line:
            product_pool = self.env['product.product'].search([('id', '=', lines.product_id.ids)])
            if lines.price_unit != product_pool.list_price:
                return True  # Go to two level approval process
            else:
                return False  # One level approval process

    double_validation = fields.Boolean('Apply Double Validation', compute="_is_double_validation_applicable")

    @api.multi
    def action_submit(self):

        is_double_validation = False

        for order in self:
            for lines in order.order_line:

                cust_commission_pool = order.env['customer.commission'].search(
                    [('customer_id', '=', order.partner_id.id), ('product_id', '=', lines.product_id.ids)])

                credit_limit_pool = order.env['res.partner'].search([('id', '=', order.partner_id.id)])

                res_partner_cred_lim = order.env['res.partner.credit.limit'].search(
                    [('partner_id', '=', order.partner_id.id),
                     ('state', '=', 'approve')], order='assign_id DESC', limit=1)

                price_change_pool = order.env['product.sale.history.line'].search(
                    [('product_id', '=', lines.product_id.id),
                     ('currency_id', '=', lines.currency_id.id),
                     ('product_package_mode', '=', order.pack_type.id),
                     ('uom_id', '=', lines.product_uom.id)])

                if order.credit_sales_or_lc == 'cash' or order.credit_sales_or_lc == 'lc_sales':
                    is_double_validation = order.second_approval_business_logics(cust_commission_pool, lines,
                                                                                 price_change_pool)
                    if is_double_validation == True:
                        break;

                elif order.credit_sales_or_lc == 'credit_sales':
                    account_receivable = credit_limit_pool.credit
                    sales_order_amount_total = -order.amount_total  # actually it should be minus value

                    customer_total_credit = account_receivable + sales_order_amount_total
                    customer_credit_limit = credit_limit_pool.credit_limit

                    if (abs(customer_total_credit) > customer_credit_limit
                        or lines.commission_rate != cust_commission_pool.commission_rate
                        or lines.price_unit != price_change_pool.new_price):

                        # Update Credit Limit and print log message
                        # if abs(customer_total_credit) < res_partner_cred_lim.value:
                        #     remaining_limit = res_partner_cred_lim.value - abs(customer_total_credit)
                        #     res_partner_cred_lim.write({'remaining_credit_limit': remaining_limit})
                        #     order.write({'remaining_credit_limit': remaining_limit})
                        # else:
                        #     res_partner_cred_lim.write({'remaining_credit_limit': '0'})
                        #     order.write({'remaining_credit_limit': '0'})

                        if res_partner_cred_lim.remaining_credit_limit == 0 \
                                and abs(customer_total_credit) < res_partner_cred_lim.value:

                                remaining_limit = res_partner_cred_lim.value - abs(customer_total_credit)
                                res_partner_cred_lim.write({'remaining_credit_limit': remaining_limit})
                                order.write({'remaining_credit_limit': remaining_limit})
                        else:
                            remaining_limit = res_partner_cred_lim.remaining_credit_limit - abs(customer_total_credit)
                            if remaining_limit < 0:

                                res_partner_cred_lim.write({'remaining_credit_limit': 0})
                                order.write({'remaining_credit_limit': 0})
                            else:
                                res_partner_cred_lim.write({'remaining_credit_limit': remaining_limit})
                                order.write({'remaining_credit_limit': remaining_limit})


                        is_double_validation = True
                        break;

                    else:
                        # Update Credit Limit and print log message
                        if res_partner_cred_lim.remaining_credit_limit == 0 \
                                and abs(customer_total_credit) < res_partner_cred_lim.value:

                                remaining_limit = res_partner_cred_lim.value - abs(customer_total_credit)
                                res_partner_cred_lim.write({'remaining_credit_limit': remaining_limit})
                                order.write({'remaining_credit_limit': remaining_limit})
                        else:
                            remaining_limit = res_partner_cred_lim.remaining_credit_limit - abs(customer_total_credit)
                            if remaining_limit < 0:

                                res_partner_cred_lim.write({'remaining_credit_limit': 0})
                                order.write({'remaining_credit_limit': 0})
                            else:
                                res_partner_cred_lim.write({'remaining_credit_limit': remaining_limit})
                                order.write({'remaining_credit_limit': remaining_limit})

                        is_double_validation = False

        if is_double_validation:
            order.write({'state': 'validate'})  # Go to two level approval process
        else:
            order.write({'state': 'done'})  # One level approval process


    def second_approval_business_logics(self, cust_commission_pool, lines, price_change_pool):
        for coms in cust_commission_pool:
            if price_change_pool.currency_id.id == lines.currency_id.id:
                for hsitry in price_change_pool:
                    if lines.commission_rate != coms.commission_rate or lines.price_unit != hsitry.new_price:
                        return True
                        break;
                    else:
                        return False


    @api.multi
    def action_create_delivery_order(self):
        view = self.env.ref('delivery_order.delivery_order_form')

        return {
            'name': ('Delivery Authorization'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'delivery.order',
            'view_id': [view.id],
            'type': 'ir.actions.act_window',
            'context': {'default_sale_order_id': self.id},
        }


    @api.multi
    @api.onchange('currency_id')
    def currency_id_onchange(self):
        self._get_changed_price()


    @api.multi
    @api.onchange('pack_type')
    def pack_type_onchange(self):
        self._get_changed_price()


    def _get_changed_price(self):
        for order in self:
            for line in order.order_line:
                vals = {}
                if line.product_id:
                    vals['price_unit'] = line._get_product_sales_price(line.product_id)
                    line.update(vals)


class InheritedSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    da_qty = fields.Float(string='DA Qty.', default=0)

    @api.one
    @api.constrains('product_uom_qty', 'commission_rate')
    def _check_order_line_inputs(self):
        if self.product_uom_qty or self.commission_rate or self.price_unit:
            if self.product_uom_qty < 0 or self.commission_rate < 0 or self.price_unit < 0:
                raise ValidationError('Price Unit, Ordered Qty & Commission Rate can not be Negative value')

            if self.order_id.product_id.commission_type == 'percentage':
                if self.commission_rate > 100:
                    raise ValidationError('Commission Rate can not be greater than 100')

    def _get_product_sales_price(self, product):

        if product:
            price_change_pool = self.env['product.sale.history.line'].search(
                [('product_id', '=', product.id),
                 ('currency_id', '=', self.order_id.currency_id.id),
                 ('product_package_mode', '=', self.order_id.pack_type.id),
                 ('uom_id', '=', self.product_uom.id)])

            if not price_change_pool:
                price_change_pool = self.env['product.sale.history.line'].search(
                    [('product_id', '=', product.id),
                     ('currency_id', '=', self.order_id.currency_id.id),
                     ('product_package_mode', '=', self.order_id.pack_type.id),
                     ('category_id', '=', self.product_uom.category_id.id)])

                if price_change_pool:
                    if not price_change_pool.uom_id.uom_type == "reference":
                        uom_base_price = price_change_pool.new_price / price_change_pool.uom_id.factor_inv
                    else:
                        uom_base_price = price_change_pool.new_price

                    if not self.product_uom.uom_type == "reference":
                        return uom_base_price * self.product_uom.factor_inv
                    else:
                        return uom_base_price
            else:
                return price_change_pool.new_price

        return 0.00

    @api.multi
    @api.onchange('product_id', 'currency_id', 'pack_type')
    def product_id_change(self):

        res = super(InheritedSaleOrderLine, self).product_id_change()
        vals = {}

        if self.product_id:
            vals['price_unit'] = self._get_product_sales_price(self.product_id)
            self.update(vals)

        return res

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        res = super(InheritedSaleOrderLine, self).product_uom_change()
        self.da_qty = self.product_uom_qty

        vals = {}
        if self.product_id:
            vals['price_unit'] = self._get_product_sales_price(self.product_id)
            self.update(vals)

        return res
