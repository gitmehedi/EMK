from odoo import fields, models, _


class InheritedProductTemplate(models.Model):
    _inherit = 'product.template'

    account_tds_id = fields.Many2one('tds.rule', string="TDS Rule", required=False,
                                     related='product_variant_ids.account_tds_id',
                                     domain="[('active', '=', True),('state', '=','confirm' )]",
                                     track_visibility='onchange')
    type = fields.Selection([
        ('consu', _('Product')),
        ('service', _('Service'))], string='Product Type', default='consu', required=True,
        help='A stockable product is a product for which you manage stock. The "Inventory" app has to be installed.\n'
             'A consumable product, on the other hand, is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.\n'
             'A digital content is a non-material product you sell online. The files attached to the products are the one that are sold on '
             'the e-commerce such as e-books, music, pictures,... The "Digital Product" module has to be installed.')


class InheritedProductProduct(models.Model):
    _inherit = 'product.product'

    account_tds_id = fields.Many2one('tds.rule', string="TDS Rule", required=False, track_visibility='onchange',
                                     domain="[('active', '=', True),('state', '=','confirm' )]")
