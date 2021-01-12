# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError


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
                # for raw materials
                if move.raw_material_production_id and move.quantity_done > 0:
                    move.product_uom_qty = move.quantity_done

    @api.multi
    def unlink(self):
        if any(move.raw_material_production_id for move in self):
            if any(move.bom_line_id for move in self):
                raise UserError(_("Sorry !!!! You cannot remove Raw Material(s) which are coming from BOM"))

            if any(move.state not in ('draft', 'confirmed', 'cancel') for move in self):
                raise UserError(_('You cannot remove Raw Materiel(s) not in confirmed state.'))

            return models.Model.unlink(self)

        return super(StockMove, self).unlink()
