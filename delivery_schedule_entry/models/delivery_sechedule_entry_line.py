from odoo import api, fields, models

class DeliveryScheduleEntryLine(models.Model):
    _name = 'delivery.schedule.entry.line'
    _description = 'Delivery Schedule Entry line'

    partner_id = fields.Many2one('res.partner', 'Customer')
    product_id = fields.Many2one('product.product')
    quantity = fields.Float(string="Ordered Qty")
    uom_id = fields.Many2one('product.uom', string="UoM")
    deli_address = fields.Char('Delivery Address')
    parent_id = fields.Many2one('delivery.schedule.entry')
    state = fields.Selection([
        ('draft', "To Submit"),
        ('validate', "To Approve"),
        ('approve', "Approved"),
    ], default='draft')
