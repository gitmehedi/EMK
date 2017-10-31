from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import amount_to_text_en
import math

class SaleOrder(models.Model):
    _inherit = "sale.order"

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
        ('da', 'Delivery Authorisation'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='to_submit')

    pack_type = fields.Many2one('product.packaging.mode',string='Packing Mode', required=True)
    currency_id = fields.Many2one("res.currency", related='', string="Currency", required=True)
    date_order=fields.Date()

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
        if self.validity_date and self.validity_date < self.date_order:
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
            #product_pool = self.env['product.product'].search([('currency_id','=',self.currency_id.id), ('id', '=', lines.product_id.ids)])
            cust_commission_pool = self.env['customer.commission'].search([('customer_id', '=', self.partner_id.id),
                                                                           ('product_id', '=', lines.product_id.ids)])
            credit_limit_pool = self.env['res.partner'].search([('id', '=', self.partner_id.id)])

            price_change_pool = self.env['product.sales.pricelist'].search([('product_id', '=', self.product_id.id),
                                                                            ('currency_id', '=', self.currency_id.id)],
                                                                           order='approver2_date desc', limit=1)

            if (self.credit_sales_or_lc == 'cash'):
                for coms in cust_commission_pool:
                    if price_change_pool.currency_id.id == lines.currency_id.id:
                        if (lines.commission_rate < coms.commission_rate
                            or lines.price_unit < price_change_pool.new_price):
                            is_double_validation = True
                            break;
                        else:
                            is_double_validation = False
                    else:
                        if (lines.commission_rate < coms.commission_rate):
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
                    or lines.price_unit < price_change_pool.new_price):

                        is_double_validation = True
                        break;
                else:
                    is_double_validation = False


            elif self.credit_sales_or_lc == 'lc_sales':
                print '-----LC-----'

        if is_double_validation:
            self.write({'state': 'validate'}) #Go to two level approval process
        else:
            self.write({'state': 'done'}) # One level approval process

    @api.multi
    def action_create_delivery_order(self):

            self.state = 'da'
            view = self.env.ref('delivery_order.delivery_order_form')

            return {
                'name': ('Delivery Authorization'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'delivery.order',
                'view_id': [view.id],
                'type': 'ir.actions.act_window',
                'context': {'default_sale_order_id': self.id},
                'state': 'DA'
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
