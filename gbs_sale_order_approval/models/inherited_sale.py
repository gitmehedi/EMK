from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import amount_to_text_en


class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines', readonly=True,
                                  copy=True)

    credit_sales_or_lc = fields.Selection([
        ('cash', 'Cash'),
        ('credit_sales', 'Credit'),
        ('lc_sales', 'L/C'),
    ], string='Sales Type', required=True)

    state = fields.Selection([
        ('to_submit', 'Submit'),
        ('draft', 'Quotation'),
        ('submit_quotation','Confirmed'),
        ('validate', 'Second Approval'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('da', 'Delivery Authorzation'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='to_submit')

    pack_type = fields.Many2one('product.packaging.mode',string='Packing Mode', required=True)
    currency_id = fields.Many2one("res.currency", related='', string="Currency", required=True)

    """ PI and LC """
    pi_no = fields.Many2one('proforma.invoice', string='PI Ref. No.')
    lc_no = fields.Many2one('letter.credit', string='LC Ref. No.')

    # @api.multi
    # def _DA_button_show_hide(self):
    #     for sale_line in self.order_line:
    #         if sale_line.product_uom_qty == sale_line.da_qty:
    #             return False
    #         else:
    #             return True
    #
    # da_button_show = fields.Boolean('DA Button show hide', compute="_DA_button_show_hide")

    @api.multi
    def amount_to_word(self, number):
        if(self.currency_id.name.encode('ascii','ignore')=='BDT'):
            return self.env['res.currency'].amount_to_word(float(number))
        else:
            currency=self.currency_id.name.encode('ascii', 'ignore')
            return amount_to_text_en.amount_to_text(number, 'en', currency)


    @api.multi
    def action_validate(self):
        self.state = 'sent'

    @api.multi
    def action_to_submit(self):
        if self.validity_date and self.validity_date <= self.date_order:
            raise UserError('Expiration Date can not be less than Order Date')

        self.state = 'draft'


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
                        if (lines.price_unit < product_pool.list_price):
                            return True  # Go to two level approval process

                    return False  # One level approval process
                elif orders.pi_no and not orders.lc_no:
                    return True  # Go to two level approval process
                else:
                    return False  # Go to two level approval process

        for lines in self.order_line:
            product_pool = self.env['product.product'].search([('id', '=', lines.product_id.ids)])
            if (lines.price_unit < product_pool.list_price):
                return True # Go to two level approval process
            else:
                return False # One level approval process

    double_validation = fields.Boolean('Apply Double Validation', compute="_is_double_validation_applicable")

    @api.multi
    def action_submit(self):

        is_double_validation = False

        for order in self:
            for lines in order.order_line:
                cust_commission_pool = order.env['customer.commission'].search([('customer_id', '=', order.partner_id.id),('product_id', '=', lines.product_id.ids)])
                credit_limit_pool = order.env['res.partner'].search([('id', '=', order.partner_id.id)])
                price_change_pool = order.env['product.sales.pricelist'].search([('product_id', '=', order.product_id.id),('currency_id', '=', order.currency_id.id)],order='approver2_date desc', limit=1)

                if (order.credit_sales_or_lc == 'cash'):
                    is_double_validation = order.second_approval_business_logics(cust_commission_pool,lines, price_change_pool)

                elif (order.credit_sales_or_lc == 'credit_sales'):
                    account_receivable = credit_limit_pool.credit
                    sales_order_amount_total = -order.amount_total #actually it should be minus value

                    customer_total_credit = account_receivable + sales_order_amount_total
                    customer_credit_limit = credit_limit_pool.credit_limit

                    if (abs(customer_total_credit) > customer_credit_limit
                        or lines.commission_rate < cust_commission_pool.commission_rate
                        or lines.price_unit < price_change_pool.new_price):

                            is_double_validation = True
                            break;
                    else:
                        is_double_validation = False

                elif order.credit_sales_or_lc == 'lc_sales':
                    # If LC and PI ref is present, go to the Final Approval, else go to Second level approval
                    if order.lc_no and order.pi_no:
                        is_double_validation = order.second_approval_business_logics(cust_commission_pool, lines, price_change_pool)
                    else:
                        is_double_validation = True

                    if order.pi_no and not order.lc_no:
                        is_double_validation = True


            if is_double_validation:
                order.write({'state': 'validate'}) #Go to two level approval process
            else:
                order.write({'state': 'sale'}) # One level approval process


    def second_approval_business_logics(self, cust_commission_pool, lines, price_change_pool):
        for coms in cust_commission_pool:
            if price_change_pool.currency_id.id == lines.currency_id.id:
                if (lines.commission_rate < coms.commission_rate
                    or lines.price_unit < price_change_pool.new_price):
                    return True
                    break;
                else:
                    return False
            else:
                if (lines.commission_rate < coms.commission_rate):
                    return True
                    break;
                else:
                    return False

    def products_price_sum(self):
        product_line_subtotal = 0
        for do_product_line in self.line_ids:
            product_line_subtotal = product_line_subtotal + do_product_line.price_subtotal

        return product_line_subtotal

    @api.multi
    def action_create_delivery_order(self):

           # self.state = 'da'
            view = self.env.ref('delivery_order.delivery_order_form')

            return {
                'name': ('Delivery Authorization'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'delivery.order',
                'view_id': [view.id],
                'type': 'ir.actions.act_window',
                'context': {'default_sale_order_id': self.id},
               # 'state': 'DA'
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
    _inherit='sale.order.line'

    #da_qty = fields.Float(string='DA Qty.', default=3)

    @api.constrains('product_uom_qty','commission_rate')
    def _check_order_line_inputs(self):
        if self.product_uom_qty or self.commission_rate:
            if self.product_uom_qty < 0 or self.commission_rate < 0 or self.price_unit < 0:
                raise ValidationError('Price Unit, Ordered Qty. & Commission Rate can not be Negative value')



    def _get_product_sales_price(self, product):

        if product:
            price_change_pool = self.env['product.sales.pricelist'].search(
                [('product_id', '=', product.id),
                 ('currency_id', '=', self.order_id.currency_id.id),
                 ('product_package_mode', '=', self.order_id.pack_type.id),
                 ('uom_id', '=', self.product_uom.id)],
                order='approver2_date desc', limit=1)

            if not price_change_pool:
                price_change_pool = self.env['product.sales.pricelist'].search(
                    [('product_id', '=', product.id),
                     ('currency_id', '=', self.order_id.currency_id.id),
                     ('product_package_mode', '=', self.order_id.pack_type.id),
                     ('category_id', '=', self.product_uom.category_id.id)],
                    order='approver2_date desc', limit=1)

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

        vals = {}
        if self.product_id:
            vals['price_unit'] = self._get_product_sales_price(self.product_id)
            self.update(vals)

        return res
