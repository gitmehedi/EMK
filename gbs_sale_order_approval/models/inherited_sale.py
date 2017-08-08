from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    credit_sales_or_lc = fields.Selection([
        ('credit_sales', 'Credit Sales'),
        ('lc_sales', 'LC Sales'),
    ], string='Sale Order Type')

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('submit_quotation','Submit Quotation'),
        ('validate', 'Second Approval'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

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
            else:
                is_double_validation = False

        if is_double_validation:
            self.write({'state': 'validate'}) #Go to two level approval process
            #self.double_validation = True
        else:
            self.write({'state': 'sent'}) # One level approval process
            #self.double_validation = False


    @api.multi
    def action_validate(self):
        self.state = 'sent'



























