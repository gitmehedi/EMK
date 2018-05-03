from odoo import api, fields, models,_

class LCPO(models.Model):
    _inherit = "letter.credit"

    po_ids = fields.Many2many('purchase.order', 'po_lc_rel', 'lc_id', 'po_id', string='Purchase Order')
    product_lines = fields.One2many('lc.product.line', 'lc_id', string='Product(s)')

    @api.onchange('po_ids')
    def po_product_line(self):
        self.product_lines = []
        vals = []
        for po_id in self.po_ids:
            for obj in po_id.order_line:
                vals.append((0, 0, {'product_id': obj.product_id,
                                    'name': obj.name,
                                    'product_qty': obj.product_qty,
                                    'price_unit': obj.price_unit,
                                    'currency_id': obj.currency_id,
                                    'date_planned': obj.date_planned,
                                    'product_uom':obj.product_uom
                                    }))
        self.product_lines = vals