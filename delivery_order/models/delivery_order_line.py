from openerp import api, fields, models, exceptions, _

class MrpDailyProductionLine(models.Model):
    _name = 'delivery.order.line'
    _description = 'Sales Delivery Order line'

    product_id = fields.Many2one('product.product', string="Product", ondelete='cascade')
    uom_id = fields.Many2one('product.uom', string="UOM",ondelete='cascade')
    quantity = fields.Integer(string="Quantity", required=True, default= "1")

    """ Relational Fields """
    parent_id = fields.Many2one('delivery.order', ondelete='cascade')
    state = fields.Selection([
        ('draft', "To Submit"),
        ('validate', "To Approve"),
        ('approve', "Second Approval"),
        ('close', "Approved")
    ], default='draft')

    pack_type = fields.Selection([
        ('cylinder', 'Cylinder'),
        ('cus_cylinder', 'Customer Cylinder'),
        ('other', 'Others'),
    ], string='Packing')

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