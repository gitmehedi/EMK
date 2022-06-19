from odoo import fields, models, api

class UtilityStockMove(models.TransientModel):
    _name = 'stock.move.utility'

    def update_move_price_unit(self, po_ids, move, _from, currency_rate):
        if _from == 'product_gate_in_window':
            for po in po_ids:
                for vb in po.invoice_ids.sorted(lambda r: r.date,reverse=True)[0]:
                    for line in vb.invoice_line_ids.sudo().search([('product_id', '=', move.product_id.id)])[0]:
                        if vb.currency_id.name == 'BDT':
                            updated_price_unit = line.price_unit
                        else:
                            if vb.conversion_rate:
                                updated_price_unit = line.price_unit * vb.conversion_rate
                        move.write({'price_unit': updated_price_unit})

        elif _from == 'landed_cost_window':
            for po in po_ids:
                for line in po.order_line.filtered(lambda l: l.product_id.id == move.product_id.id):
                    po_price_unit = line.price_unit
                    updated_move_price_unit = po_price_unit * currency_rate

                    # update all moves same to origin
                    moves = self.env['stock.move'].sudo().search(
                        [('origin', '=', move.origin), ('product_id', '=', line.product_id.id)])
                    for a_move in moves:
                        a_move.write({'price_unit': updated_move_price_unit})

