from odoo import api, fields, models
import time, datetime


class DeliveryJarCount(models.Model):
    _name = 'delivery.jar.count'
    _description = 'Delivery Jar Count'
    #_inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "id desc"

    partner_id = fields.Many2one('res.partner', string='Partner')
    product_id = fields.Many2one('product.product', string='Product')
    challan_id = fields.Many2one('stock.picking', string='Challan Id')
    uom_id = fields.Many2one('product.uom', string='UoM')
    jar_count = fields.Integer(string='# of Jar')
    packing_mode_id = fields.Many2one('product.packaging.mode', string='Packaging Mode')
    jar_type = fields.Char(string='Jar Type')
    date = fields.Date(string='Date')





