from odoo import api, fields, models,_


class LCProduct(models.Model):
    # _inherit = "purchase.order.line"
    _name = 'lc.product.line'
    _description = 'Product'
    _order = "date_planned desc"

    name = fields.Text(string='Description', required=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)],
                                 change_default=True, required=True)

    product_qty = fields.Float(string='LC Quantity')
    product_received_qty = fields.Float(string='Received Quantity')
    price_unit = fields.Float(string='Unit Price')
    currency_id = fields.Many2one('res.currency', 'Currency')
    date_planned = fields.Datetime(string='Scheduled Date', index=True)
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure')

    lc_id = fields.Many2one('letter.credit', string='LC')

class LCPO(models.Model):
    _inherit = "letter.credit"

    po_ids = fields.Many2many('purchase.order', 'po_lc_rel', 'lc_id', 'po_id', string='Purcahse Order')
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