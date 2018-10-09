from odoo import fields, models


class InheritedProductProduct(models.Model):
    _inherit = 'product.product'


    #relatinal fields
    product_income_acc = fields.One2many('product.income.acc.conf', 'parent_id', string="Income Account",)


