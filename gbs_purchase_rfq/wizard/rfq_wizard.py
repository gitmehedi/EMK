from odoo import api, fields, models, _



class RFQWizard(models.TransientModel):
    _name = 'rfq.wizard'

    product_lines = fields.One2many('rfq.product.line.wizard', 'rfq_id', string='Product(s)')

    pr_ids = fields.Many2many('purchase.requisition', string='PR',
                                  default=lambda self: self.env.context.get('active_ids'))

    @api.onchange('pr_ids')
    def _compute_product_lines(self):
        # self.product_lines = []
        if self.pr_ids:
            vals = []
            # form_ids = self.env.context.get('active_ids')
            line_pool = self.env['purchase.requisition.line'].search([('requisition_id', 'in', self.pr_ids.ids)])
            for obj in line_pool:
                # product_qty = obj.product_qty - obj.product_received_qty
                # if product_qty > 0:
                vals.append((0, 0, {'product_id': obj.product_id,
                                    # 'pr_line_id': obj.id,
                                    # 'name': obj.name,
                                    'product_qty': obj.product_qty,
                                    'product_uom_id': obj.product_uom_id.id,
                                    'price_unit': obj.price_unit,
                                    }))
            self.product_lines = vals



class ShipmentProductLineWizard(models.TransientModel):
    _name = 'rfq.product.line.wizard'

    rfq_id = fields.Many2one('rfq.wizard', string='RFQ', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True, ondelete='cascade')
    product_qty = fields.Float(string='Quantity')
    price_unit = fields.Float(string='Price Unit')
    product_uom_id = fields.Many2one('product.uom', string='Unit of Measure')
