from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    currency_id = fields.Many2one("res.currency", string="Currency", required=True)

    credit_sales_or_lc = fields.Selection([
        ('cash', 'Cash'),
        ('credit_sales', 'Credit'),
        ('lc_sales', 'L/C'),
    ], string='Sale Order Type', required=True)

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('submit_quotation','Confirmed'),
        ('validate', 'Second Approval'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    pack_type = fields.Many2one('product.packaging.mode',string='Packing Mode', required=True)

    #uom_id = fields.Many2one('product.uom', string="UoM", domain=[('category_id', '=', 2)], required=True)

    @api.multi
    def action_validate(self):
        self.state = 'sent'

    @api.multi
    def _is_double_validation_applicable(self):
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

        for lines in self.order_line:
            product_pool = self.env['product.product'].search([('id', '=', lines.product_id.ids)])
            cust_commission_pool = self.env['customer.commission'].search([('customer_id', '=', self.partner_id.id),
                                                                           ('product_id', '=', lines.product_id.ids)])
            credit_limit_pool = self.env['res.partner'].search([('id', '=', self.partner_id.id)])

            if (self.credit_sales_or_lc == 'cash'):
                for coms in cust_commission_pool:
                    if (lines.commission_rate < coms.commission_rate
                        or lines.price_unit < product_pool.list_price):
                        is_double_validation = True
                        break;
                    else:
                        is_double_validation = False

            elif (self.credit_sales_or_lc == 'credit_sales'):
                account_receivable = credit_limit_pool.credit
                sales_order_amount_total = -self.amount_total #actually it should be minus value

                customer_total_credit = account_receivable + sales_order_amount_total
                customer_credit_limit = credit_limit_pool.credit_limit

                if (abs(customer_total_credit) > customer_credit_limit
                    or lines.commission_rate < cust_commission_pool.commission_rate
                    or lines.price_unit < product_pool.list_price):

                        is_double_validation = True
                        break;
                else:
                    is_double_validation = False


            elif self.credit_sales_or_lc == 'lc_sales':
                print '-----LC-----'

        if is_double_validation:
            self.write({'state': 'validate'}) #Go to two level approval process
        else:
            self.write({'state': 'sent'}) # One level approval process

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
            'context': {'default_sale_order_id': self.id}
        }

    @api.multi
    @api.onchange('pack_type')
    def pack_type_onchange(self):
        for order in self:
            for line in order.order_line:
                vals = {}
                if line.product_id:
                    vals['price_unit'] = line._get_product_sales_price(line.product_id)
                    line.update(vals)

        # self.update_onchanged_product_price()

    # @api.onchange('currency_ids')
    # def currency_ids_onchange(self):
    #     self.update_onchanged_currency_id()

    # def update_onchanged_product_price(self):
    #
    #     if self.product_id:
    #
    #         price_change_pool = self.env['product.sales.pricelist'].search([('product_id', '=', self.product_id.id),
    #                                                                   ('currency_id', '=', self.currency_ids.id),
    #                                                                   ('product_package_mode', '=', self.pack_type.id)],
    #                                                                  order='approver2_date desc', limit=1)
    #
    #         line_pol = self.env['sale.order.line.temp'].search([('pack_type','=',self.pack_type.id),
    #                                                             ('product_id','=',self.order_line.product_id.id)],
    #                                                            order='create_date desc', limit=1)
    #
    #
    #         price_pool_len = len(price_change_pool)
    #
    #         vals = {}
    #
    #         if price_pool_len == 1:
    #             vals['price_unit'] = price_change_pool.new_price
    #             vals['product_uom'] = price_change_pool.uom_id.id
    #             vals['product_id'] = price_change_pool.product_id.id
    #
    #             if price_change_pool.uom_id.name != self.order_line.product_uom.name:
    #                pass
    #             else:
    #                 vals['price_unit'] = line_pol.price_unit
    #                 vals['product_uom'] = line_pol.product_uom
    #                 vals['product_id'] =  price_change_pool.product_id.id
    #
    #         elif price_pool_len > 1:
    #             for price_pol in price_change_pool:
    #                 vals['price_unit'] = price_pol.new_price
    #         elif price_pool_len == 0:
    #             product_pool = self.env['product.product'].search([('id', '=', self.product_id.id)])
    #             vals['price_unit'] = product_pool.list_price
    #
    #         self.order_line.pricelist_id = None
    #         self.order_line.partner_id = None
    #
    #         self.order_line.update(vals)
    #


    # def update_onchanged_currency_id(self):
    #
    #     if self.product_id:
    #
    #         price_change_pool = self.env['product.sales.pricelist'].search([('product_id', '=', self.product_id.id),
    #                                                                   ('currency_id', '=', self.currency_ids.id),
    #                                                                   ('product_package_mode', '=', self.pack_type.id)],
    #                                                                  order='approver2_date desc', limit=1)
    #
    #
    #         price_pool_len = len(price_change_pool)
    #
    #         vals = {}
    #
    #         if price_pool_len == 1:
    #             vals['price_unit'] = price_change_pool.new_price
    #         elif price_pool_len > 1:
    #             for price_pol in price_change_pool:
    #                 vals['price_unit'] = price_pol.new_price
    #         elif price_pool_len == 0:
    #             product_pool = self.env['product.product'].search([('id', '=', self.product_id.id)])
    #             vals['price_unit'] = product_pool.list_price
    #
    #         self.order_line.pricelist_id = None
    #         self.order_line.partner_id = None
    #
    #         self.order_line.update(vals)
    #

class InheritedSaleOrderLine(models.Model):
    _inherit='sale.order.line'

    # @api.onchange('product_uom', 'product_uom_qty')
    # def product_uom_change(self):
    #
    #     if self.product_uom:
    #         product_pool = self.env['product.product'].search([('id', '=', self.order_id.product_id.id)])
    #         price_change_pool = self.env['product.sales.pricelist'].search([('product_id', '=', self.product_id.id),
    #                                                                         ('currency_id', '=',  product_pool.currency_id.id),],
    #                                                                        order='approver2_date desc', limit=1)
    #
    #         if price_change_pool.uom_id.id == self.product_uom.id:
    #             self.price_unit = price_change_pool.new_price
    #             return
    #
    #         if self.product_uom.uom_type == 'smaller':
    #             self.price_unit = (self.price_unit / self.product_uom.factor) / 1000
    #         elif self.product_uom.uom_type == 'bigger':
    #             self.price_unit = self.price_unit * self.product_uom.factor
    #         elif self.product_uom.uom_type == 'reference':
    #             self.price_unit = self.price_unit / 1000
    #
    #         self.amount_untaxed = self.price_unit
    #         self.amount_tax = (self.tax_id.amount * self.price_unit) / 100
    #         self.price_subtotal = self.price_unit * self.product_uom_qty
    #
    #         line_temp = {}
    #         line_temp['price_unit'] = self.price_unit
    #         line_temp['product_uom'] = self.product_uom.id
    #         line_temp['product_id'] = self.product_id.id
    #         line_temp['pack_type'] = self.order_id.pack_type.id
    #
    #         self.env['sale.order.line.temp'].create(line_temp)
    #
    #

    # @api.one
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
                    # elif price_change_pool.uom_id.uom_type == "smaller":
                    #     uom_base_price = price_change_pool.new_price * price_change_pool.uom_id.factor_inv
                    else:
                        uom_base_price = price_change_pool.new_price

                    if not self.product_uom.uom_type == "reference":
                        return uom_base_price * self.product_uom.factor_inv
                    # elif self.product_uom.uom_type == "smaller":
                    #     return uom_base_price / self.product_uom.factor_inv
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

        # if self.product_id:
        #
        #     price_change_pool = self.env['product.sales.pricelist'].search([('product_id', '=', self.order_id.product_id.id),
        #                                                               ('currency_id', '=', self.order_id.currency_ids.id),
        #                                                               ('product_package_mode', '=', self.order_id.pack_type.id),
        #                                                               ('uom_id', '=', self.product_uom.id)],
        #                                                              order='approver2_date desc', limit=1)
        #
        #     price_pool_len = len(price_change_pool)
        #
        #     vals = {}
        #
        #     if price_pool_len == 1:
        #         vals['price_unit']  = price_change_pool.new_price
        #     elif price_pool_len > 1:
        #         for price_pol in price_change_pool:
        #             vals['price_unit'] = price_pol.new_price
        #     elif price_pool_len == 0:
        #         product_pool = self.env['product.product'].search([('id', '=', self.product_id.id)])
        #         vals['price_unit']  = product_pool.list_price
        #
        #     self.order_id.pricelist_id = None
        #     self.order_id.partner_id = None
        #
        #     self.update(vals)
        #     res = super(InheritedSaleOrderLine, self).product_id_change()



class SaleOrderLineTemp(models.Model):
    _name = 'sale.order.line.temp'

    product_id = fields.Integer()
    price_unit = fields.Float()
    product_uom = fields.Integer()
    pack_type = fields.Integer()
