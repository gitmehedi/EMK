from odoo import api, fields, models,_


class ResetLCWizard(models.TransientModel):
    _name = 'reset.lc.wizard'

    product_lines = fields.One2many('reset.lc.product.wizard', 'reset_lc_wizard_id', string='Product(s)')
    shipment_id = fields.Many2one('purchase.shipment', string='Purchase Shipment',
                                  default=lambda self: self.env.context.get('active_id'))

    @api.onchange('shipment_id')
    def po_product_line(self):
        self.product_lines = []
        vals = []
        pro_lc_line_pool = self.env['lc.product.line'].search([('lc_id', '=', self.shipment_id.lc_id.id)])
        for obj in pro_lc_line_pool:
            # product_qty = obj.product_qty - obj.product_received_qty
            # if product_qty > 0:
            vals.append((0, 0, {'product_id': obj.product_id,
                                'lc_pro_line_id': obj.id,
                                'name': obj.name,
                                'product_qty': obj.product_qty,
                                'currency_id': obj.currency_id,
                                'date_planned': obj.date_planned,
                                'product_uom': obj.product_uom,
                                'price_unit': obj.price_unit,
                                'product_received_qty': obj.product_received_qty,
                                }))
        self.product_lines = vals


    def save_lc_line(self):
        for pro_line in self.product_lines:
            pro_lc_line_pool = self.env['lc.product.line'].search([('id', '=', pro_line.lc_pro_line_id)])
            pro_lc_line_pool.write({'product_received_qty':pro_line.product_received_qty})

        self.shipment_id.shipment_product_lines.unlink()
        self.shipment_id.write({'state': 'draft'})

        return {'type': 'ir.actions.act_window_close'}


class ResetLCProductWizard(models.TransientModel):
    _name = 'reset.lc.product.wizard'

    reset_lc_wizard_id = fields.Many2one('reset.lc.wizard', string='Reset LC', ondelete='cascade')
    name = fields.Text(string='Description', required=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)],
                                 change_default=True, required=True)

    product_qty = fields.Float(string='LC Quantity')
    product_received_qty = fields.Float(string='Document Qty')
    price_unit = fields.Float(string='Unit Price')
    currency_id = fields.Many2one('res.currency', 'Currency')
    date_planned = fields.Datetime(string='Scheduled Date', index=True)
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure')
    lc_pro_line_id = fields.Integer(string='LC Line ID')
