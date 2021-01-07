# imports of odoo
from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    standard_qty = fields.Float(string='Standard Qty', readonly=True)
    check_to_done = fields.Boolean(compute='_compute_check_to_done')

    @api.depends('raw_material_production_id.check_to_done')
    def _compute_check_to_done(self):
        for move in self:
            move.check_to_done = move.raw_material_production_id.check_to_done

    @api.multi
    def _qty_done_set(self):
        """Override _qty_done_set to update the value of product_uom_qty field"""
        for move in self:
            if move.has_tracking == 'none':
                move.quantity_done_store = move.quantity_done
                move.product_uom_qty = move.quantity_done
