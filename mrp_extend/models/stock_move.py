# imports of odoo
from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    standard_qty = fields.Float(string='Standard Quantity', required=True, readonly=True)
