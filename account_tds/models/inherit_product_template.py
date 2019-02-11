from odoo import fields, models


class InheritedProductTemplate(models.Model):
    _inherit = 'product.template'

    account_tds_id = fields.Many2one('tds.rule', string="TDS Rule", required=True,related='product_variant_ids.account_tds_id',
                                     domain="[('active', '=', True),('state', '=','confirm' )]")

class InheritedProductProduct(models.Model):
    _inherit = 'product.product'

    account_tds_id = fields.Many2one('tds.rule', string="TDS Rule", required=True,
                                     domain="[('active', '=', True),('state', '=','confirm' )]")