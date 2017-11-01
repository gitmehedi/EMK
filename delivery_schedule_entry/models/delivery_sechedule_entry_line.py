from odoo import api, fields, models

class DeliveryScheduleEntryLine(models.Model):
    _name = 'delivery.schedule.entry.line'
    _description = 'Delivery Schedule Entry line'

    partner_id = fields.Many2one('res.partner', 'Customer',domain="([('customer','=','True')])")
    product_id = fields.Many2one('product.product','Products',required=True)
    quantity = fields.Float(string="Ordered Qty")
    uom_id = fields.Many2one('product.uom', string="UoM")
    pack_type = fields.Many2one('product.packaging.mode', string="Packing",ondelete='cascade')
    deli_address = fields.Char('Delivery Address')
    parent_id = fields.Many2one('delivery.schedule.entry')
    remarks = fields.Char('Remarks')
    state = fields.Selection([
        ('draft', "To Submit"),
        ('approve', "Confirm"),
    ], default='draft')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            product_obj = self.env['product.template'].search([('id', '=', self.product_id.id)])
            if product_obj:
                self.uom_id = product_obj.uom_id.id


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.parent_id:
            customer_obj = self.env['res.partner'].search([('id', '=', self.partner_id.id)])
            if customer_obj:
                self.deli_address = customer_obj.street