from odoo import api, fields, models, _


class FineshProduct(models.Model):
    _name = 'finish.product.line'

    product_id = fields.Many2one('product.template', 'Product Name')
    daily_pro_id = fields.Many2one('daily.production', 'Daily Production')
    fnsh_product_qty = fields.Float('Quantity')
    date = fields.Date('Date')
    uom_id = fields.Many2one('product.uom', 'UOM')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('reset', 'Reset To Draft'),
    ], string='Status', default='draft')

    @api.onchange('product_id')
    def po_product_line(self):
        self.daily_pro_id.consumed_product_line_ids = []

        vals = []
        if self.product_id:
            pro_line_pool = self.env['mrp.bom'].search(
                [('product_tmpl_id', '=', self.product_id.id)])
            for obj in pro_line_pool.bom_line_ids:
                vals.append((0, 0, {
                                    'product_id': obj.product_id.id,
                                    'con_product_qty': obj.product_qty,

                                    }))

                self.daily_pro_id.consumed_product_line_ids = vals