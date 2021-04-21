# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class StockMove(models.Model):
    _inherit = 'stock.move'

    quantity_done_store = fields.Float(digits=dp.get_precision('Product Unit of Measure'))

    standard_qty = fields.Float(string='Standard Qty', readonly=True, digits=dp.get_precision('Product Unit of Measure'))
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
    def move_validate(self):
        moves_todo = super(StockMove, self).move_validate()
        if moves_todo:
            date_planned_start = moves_todo[0].production_id.date_planned_start or moves_todo[0].raw_material_production_id.date_planned_start
            if date_planned_start:
                moves_todo.write({'date': date_planned_start})

        return moves_todo

    @api.multi
    def unlink(self):
        if any(move.raw_material_production_id for move in self):
            if any(move.bom_line_id for move in self):
                raise UserError(_("Sorry !!!! You cannot remove Raw Material(s) which are coming from BOM"))

            if any(move.state not in ('draft', 'confirmed', 'cancel') for move in self):
                raise UserError(_('You cannot remove Raw Materiel(s) not in confirmed state.'))

            return models.Model.unlink(self)

        return super(StockMove, self).unlink()
