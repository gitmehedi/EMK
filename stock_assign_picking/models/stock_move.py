from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = "stock.move"

    # @api.multi
    # def assign_picking(self):
    #

