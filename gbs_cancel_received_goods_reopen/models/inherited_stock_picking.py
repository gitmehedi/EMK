# import of odoo
from odoo import models, fields, api, _


class InheritStockPickingReopen(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_reopen(self):
        picking_id = self.id
        moves_obj = self.env['stock.move'].search([('picking_id', '=', picking_id)])
        picking_obj = self.env['stock.picking'].browse(picking_id)

        if moves_obj:
            for move in moves_obj:
                if move.state == 'cancel':
                    move.state = 'draft'

        picking_obj.action_confirm()

    def action_qc_sound_stock_cancel_reopen(self):
        picking_id = self.id
        moves_obj = self.env['stock.move'].search([('picking_id', '=', picking_id)])
        picking_obj = self.env['stock.picking'].browse(picking_id)

        if moves_obj:
            for move in moves_obj:
                if move.state == 'cancel':
                    if move.location_dest_id.name == 'Stock':
                        move.state = 'confirmed'
                        picking_obj.recheck_availability()
                    elif move.location_dest_id.name == 'Quality Control':
                        move.state = 'draft'
                        picking_obj.action_confirm()
                        picking_obj.recheck_availability()
