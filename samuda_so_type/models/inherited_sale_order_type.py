from odoo import fields, models


class InheritedSaleOrderType(models.Model):
    _inherit = 'sale.order.type'

    operating_unit = fields.Many2one('operating.unit', string="Operating Unit", required=True)
    sale_order_type = fields.Selection([
        ('cash', 'Cash'),
        ('credit_sales', 'Credit'),
        ('lc_sales', 'L/C'),
    ], string='Sale Order Type', required=True)

    currency_id = fields.Many2one('res.currency', string="Currency", required=True)
