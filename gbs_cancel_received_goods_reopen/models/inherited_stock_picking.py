# import of odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

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
                    if move.location_dest_id.name == 'Quality Control':
                        query = """select sl.name,sp.state from stock_picking as sp LEFT JOIN stock_move as sm ON sp.id=sm.picking_id 
                                                                LEFT JOIN stock_location as sl ON sl.id=sm.location_dest_id
                                                                where sm.origin='%s' and sp.state !='done' and sl.name='Stock'""" % move.origin
                        self.env.cr.execute(query)
                        is_reopen_msg = True
                        for row in self.env.cr.dictfetchall():
                            if row['state'] != 'cancel':
                                is_reopen_msg = False
                                break

                        if is_reopen_msg:
                            raise UserError(_("Sound Stock has cancel stock transfer, please reopen first"))

                        move.state = 'draft'
                        picking_obj.action_confirm()
                        picking_obj.recheck_availability()

                    elif move.location_dest_id.name == 'Stock':
                        move.state = 'confirmed'
                        picking_obj.recheck_availability()

                    elif move.location_dest_id.name == 'Customers':
                        move.state = 'confirmed'
