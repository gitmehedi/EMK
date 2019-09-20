from odoo import api, fields, models


class CustomerCommissionLine(models.Model):
    _name = "customer.commission.line"
    _order='status desc, effective_date desc'

    effective_date = fields.Date(string='Effective Date', required=True)
    commission_rate = fields.Float(string='Commission', digits=(16, 2), required=True)
    status = fields.Boolean(string='Active Rate', default=True, required=True)

    """ Relational Fields """

    product_id = fields.Many2one('product.product', string='Product', ondelete='cascade')
    customer_id = fields.Many2one('res.partner', string='Customer', ondelete='cascade')
    commission_id = fields.Many2one('customer.commission', string='Commission', ondelete='cascade')
