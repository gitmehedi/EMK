from odoo import fields, models,api
from odoo.exceptions import UserError, ValidationError

class InheritedSaleOrderType(models.Model):
    _inherit = 'sale.order.type'

    operating_unit = fields.Many2one('operating.unit', string="Operating Unit", required=True)
    sale_order_type = fields.Selection([
        ('cash', 'Cash'),
        ('credit_sales', 'Credit'),
        ('lc_sales', 'L/C'),
    ], string='Sale Order Type', required=True)

    currency_id = fields.Many2one('res.currency', string="Currency", required=True)

    @api.constrains('name')
    def _check_unique_name(self):
        name = self.env['sale.order.type'].search([('name', '=', self.name)])
        if len(name) > 1:
            raise ValidationError('Customer already exists.')
