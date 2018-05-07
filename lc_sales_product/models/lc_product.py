from odoo import api, fields, models,_

class LCSO(models.Model):
    _inherit = "letter.credit"

    so_ids = fields.Many2many('sale.order', 'so_lc_rel', 'lc_id', 'so_id', string='Sale Order')
    product_lines = fields.One2many('lc.product.line', 'lc_id', string='Product(s)')

    # so_ids = fields.One2many('sale.order', 'lc_id', string='Sale Order')

    # so_ids_temp = fields.Many2many('sale.order', 'so_lc_rel', 'lc_id', 'so_id', string='Sale Order')

    @api.onchange('so_ids')
    def so_product_line(self):
        self.product_lines = []
        vals = []
        for so_id in self.so_ids:
            for obj in so_id.order_line:
                vals.append((0, 0, {'product_id': obj.product_id,
                                    'name': obj.name,
                                    'product_qty': obj.product_uom_qty,
                                    'price_unit': obj.price_unit,
                                    'currency_id': obj.currency_id,
                                    'product_uom':obj.product_uom
                                    }))
        self.product_lines = vals