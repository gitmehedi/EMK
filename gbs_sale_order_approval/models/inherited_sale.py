from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

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
    currency_ids = fields.Many2one('res.currency', string="Currency", required=True)
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

    @api.onchange('pack_type')
    def pack_type_onchange(self):
        self.update_onchanged_product_price()

    @api.onchange('currency_ids')
    def currency_ids_onchange(self):
        self.update_onchanged_product_price()


    def update_onchanged_product_price(self):

        if self.product_id:

            price_change_pool = self.env['product.sales.pricelist'].search([('product_id', '=', self.product_id.id),
                                                                      ('currency_id', '=', self.currency_ids.id),
                                                                      ('product_package_mode', '=', self.pack_type.id)],
                                                                     order='approver2_date desc', limit=1)

            price_pool_len = len(price_change_pool)

            vals = {}

            if price_pool_len == 1:
                vals['price_unit'] = price_change_pool.new_price
            elif price_pool_len > 1:
                for price_pol in price_change_pool:
                    vals['price_unit'] = price_pol.new_price
            elif price_pool_len == 0:
                product_pool = self.env['product.product'].search([('id', '=', self.product_id.id)])
                vals['price_unit'] = product_pool.list_price

            self.order_line.pricelist_id = None
            self.order_line.partner_id = None

            self.order_line.update(vals)


class InheritedSaleOrderLine(models.Model):
    _inherit='sale.order.line'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):

        if self.product_id:

            price_change_pool = self.env['product.sales.pricelist'].search([('product_id', '=', self.order_id.product_id.id),
                                                                      ('currency_id', '=', self.order_id.currency_ids.id),
                                                                      ('product_package_mode', '=', self.order_id.pack_type.id),
                                                                      ('uom_id', '=', self.product_uom.id)],
                                                                     order='approver2_date desc', limit=1)

            price_pool_len = len(price_change_pool)

            vals = {}

            if price_pool_len == 1:
                vals['price_unit']  = price_change_pool.new_price
            elif price_pool_len > 1:
                for price_pol in price_change_pool:
                    vals['price_unit'] = price_pol.new_price
            elif price_pool_len == 0:
                product_pool = self.env['product.product'].search([('id', '=', self.product_id.id)])
                vals['price_unit']  = product_pool.list_price

            self.order_id.pricelist_id = None
            self.order_id.partner_id = None

            self.update(vals)
            res = super(InheritedSaleOrderLine, self).product_id_change()

