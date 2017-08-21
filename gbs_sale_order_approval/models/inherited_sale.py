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
    def _is_double_validation_applicable(self):
        for lines in self.order_line:
            product_pool = self.env['product.product'].search([('product_tmpl_id', '=', lines.product_id.ids)])
            if (lines.price_unit < product_pool.list_price):
                return True # Go to two level approval process
            else:
                return False # One level approval process

    double_validation = fields.Boolean('Apply Double Validation', compute="_is_double_validation_applicable")

    @api.multi
    def action_submit(self):
        #@Todo: Need to add checkings for Customer Commission, Customer Credit Limit and type of Sale Order i.e. LC/Credit
        is_double_validation = None
        for lines in self.order_line:
            product_pool = self.env['product.product'].search([('product_tmpl_id', '=', lines.product_id.ids)])
            if (lines.price_unit < product_pool.list_price):
                is_double_validation = True
                break;
            else:
                is_double_validation = False

        if is_double_validation:
            self.write({'state': 'validate'}) #Go to two level approval process
        else:
            self.write({'state': 'sent'}) # One level approval process


    @api.multi
    def action_validate(self):
        self.state = 'sent'

