from odoo import api, fields, models


class CustomerCommissionConfiguration(models.Model):
    _name="customer.commission.configuration"
    _order='confirmed_date desc'


    requested_date= fields.Date(string="Requested Date")
    approved_date= fields.Date(string="Approved Date")
    confirmed_date = fields.Date(string="Confirmed Date")

    status = fields.Boolean(string='Status',default=True, required=True)

    commission_type = fields.Selection([
        ('by_product', 'By Product'),
        ('by_customer', 'By Customer')
    ], default='by_product', string='Commission Type', required=True)


    """ Relational Fields """
    product_id = fields.Many2one('product.product', string="Product")

    customer_id = fields.Many2one('res.partner', string="Customer")
    requested_by_id = fields.Many2one('res.partner', string="Requested By")
    approved_user_id = fields.Many2one('res.partner', string="Approved By")
    confirmed_user_id = fields.Many2one('res.partner', string="Confirmed By")

    config_product_ids = fields.One2many('customer.commission.configuration.product', 'config_parent_id')
    config_customer_ids = fields.One2many('customer.commission.configuration.customer', 'config_parent_id')

