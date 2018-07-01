from odoo import fields, models

class InheritedProductTemplate(models.Model):
    _inherit='product.template'

    commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed')
    ], string='Commission Type',default='percentage')

