from odoo import api, fields, models, exceptions, _

class MrpDailyProductionLine(models.Model):
    _name = 'delivery.order.line'
    _description = 'Sales Delivery Order line'

    product_id = fields.Many2one('product.product', string="Product", readonly=True, ondelete='cascade')
    uom_id = fields.Many2one('product.uom', string="UoM",ondelete='cascade',readonly=True)
    pack_type = fields.Many2one('product.packaging.mode', string="Packing",ondelete='cascade',readonly=False)
    quantity = fields.Integer(string="Ordered Qty", required=True, default= "1",readonly=True)
    price_unit = fields.Float(string="Price Unit")
    commission_rate = fields.Float(string="Com. (%)")
    price_subtotal = fields.Float(string="Subtotal")


    """ Relational Fields """
    parent_id = fields.Many2one('delivery.order', ondelete='cascade')
    state = fields.Selection([
        ('draft', "To Submit"),
        ('validate', "To Approve"),
        ('approve', "Second Approval"),
        ('close', "Approved")
    ], default='draft')


    deli_mode = fields.Selection([
        ('bonded', 'Bonded'),
        ('non_bonded', 'Non-bonded'),
        ('vat', 'VAT'),
    ], string='Delivery Mode')


    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            product_obj = self.env['product.template'].search([('id', '=', self.product_id.id)])
            if product_obj:
                self.uom_id = product_obj.uom_id.id