from openerp import api, fields, models, exceptions, _

class MrpDailyProductionLine(models.Model):
    _name = 'delivery.order.line'
    _description = 'Sales Delivery Order line'

    product_id = fields.Many2one('product.template', string="Product", ondelete='cascade')
    uom_id = fields.Many2one('product.uom', string="UOM",ondelete='cascade')
    quantity = fields.Integer(string="Quantity", required=True)

    """ Relational Fields """
    parent_id = fields.Many2one('delivery.order', ondelete='cascade')
    state = fields.Selection([
        ('draft', "Draft"),
        ('applied', "Applied"),
        ('approved', "Approved"),
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

