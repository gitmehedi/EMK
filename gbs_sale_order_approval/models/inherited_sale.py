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

    pack_type = fields.Selection([
        ('cylinder', 'Cylinder'),
        ('cust_cylinder', 'Customer Cylinder'),
        ('other', 'Others'),
    ], string='Packing',required=True)

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