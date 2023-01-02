from odoo import fields, models, api


class InheritedStockPicking(models.Model):
    _inherit = 'stock.picking'

    name = fields.Char()
