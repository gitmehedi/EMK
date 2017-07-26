from odoo import api, fields, models


class CustomerCommissionConfigurationProduct(models.Model):
    _name="customer.commission.configuration.product"
    _order='id desc'

    old_value= fields.Float(string="Old Value", digits=(16,2), readonly=True)
    new_value= fields.Float(string="New Value", digits=(16,2), required=True)
    status = fields.Boolean(string='Status',default=True, required=True)

    """ Relational Fields """
    product_id = fields.Many2one('product.product', string="Product", required=True)
    config_parent_id = fields.Many2one('customer.commission.configuration', ondelete='cascade')

