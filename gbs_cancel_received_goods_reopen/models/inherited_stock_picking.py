# import of odoo
from odoo import models, fields, api,_


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



