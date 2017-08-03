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


    def _is_double_validation_applicable(self):
        for lines in self.order_line:
            product_pool = self.env['product.product'].search([('product_tmpl_id', '=', lines.product_id.id)])
            if (lines.price_unit > product_pool.list_price):
                return True ## Apply Double validaion
            else:
                return False ## Single Validation

    double_validation = fields.Boolean('Apply Double Validation', default=_is_double_validation_applicable)

    @api.multi
    def action_submit(self):

        # Business logic to apply double validation approval process
        is_double_validation = None
        for lines in self.order_line:
            product_pool = self.env['product.product'].search([('product_tmpl_id', '=', lines.product_id.ids)])
            if (lines.price_unit < product_pool.list_price):
                is_double_validation = True
            else:
                is_double_validation = False

        if is_double_validation:
            self.write({'state': 'validate'}) #Go to two level approval process
        else:
            self.write({'state': 'sent'}) # One level approval process



    @api.multi
    def action_validate(self):
        self.state = 'sent'


























