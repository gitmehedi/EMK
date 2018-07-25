from odoo import api, fields, models,_


class LCProduct(models.Model):
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

    delivered_qty =  fields.Float(string='Delivered',compute = '_compute_delivered_qty',store=False)

    @api.multi
    def _compute_delivered_qty(self):
        for product in self:
            so_ids = self.env['sale.order'].search([('lc_id', '=', product.lc_id.id)])
            for so_id in so_ids:
                quantity = so_id.order_line.filtered(lambda x: x.product_id.id == product.product_id.id).qty_delivered
                product.delivered_qty = product.delivered_qty + quantity