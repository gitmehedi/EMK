from odoo import fields, models, api


class InheritedStockMove(models.Model):
    _inherit = 'stock.move'

    available_qty = fields.Float(string="Available Quantity")