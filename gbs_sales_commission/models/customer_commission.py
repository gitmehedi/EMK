from odoo import api, fields, models


class CustomerCommission(models.Model):
    _name="customer.commission"


    commission_rate = fields.Float(string='Commission Rate', digits=(16,2), required=True)
    status = fields.Boolean(string='Status',default=True, required=True)

    """ Relational Fields """

    product_id = fields.Many2one('product.product', string='Product', ondelete='cascade')
    customer_id = fields.Many2one('res.partner', string="Customer", ondelete='cascade')
    line_ids = fields.One2many('customer.commission.line','commission_id')


