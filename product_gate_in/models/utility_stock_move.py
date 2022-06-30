from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class UtilityStockMove(models.TransientModel):
    _name = 'stock.move.utility'

    def update_move_price_unit(self, po_ids, move, _from, currency_rate, shipment_rate):
        if _from == 'product_gate_in_window':
            for po in po_ids:
                if po.invoice_ids:
                    for vb in po.invoice_ids.sorted(lambda r: r.date, reverse=True)[0]:
                        for line in vb.invoice_line_ids.sudo().search([('product_id', '=', move.product_id.id)])[0]:
                            if vb.currency_id.name == 'BDT':
                                updated_price_unit = line.price_unit
                            else:
                                if vb.conversion_rate:
                                    updated_price_unit = line.price_unit * vb.conversion_rate
                            move.write({'price_unit': updated_price_unit})

        elif _from == 'landed_cost_window':
            # updated_move_price_unit = move.price_unit / shipment_rate
            move.write({'price_unit': shipment_rate * currency_rate})
            # for po in po_ids:
            #     for line in po.order_line.filtered(lambda l: l.product_id.id == move.product_id.id):
            #         po_price_unit = line.price_unit
            #         updated_move_price_unit = po_price_unit * currency_rate
            #
            #         # update all moves same to origin
            #         moves = self.env['stock.move'].sudo().search(
            #             [('origin', '=', move.origin), ('product_id', '=', line.product_id.id)])
            #         for a_move in moves:
            #             a_move.write({'price_unit': updated_move_price_unit})
        elif _from == 'landed_cost_window_2':
            move.write({'price_unit': currency_rate})

    def get_po_unit_price(self, product_id, lc):
        if lc.po_ids:
            for po in lc.po_ids:
                for line in po.order_line:
                    if line.product_id.id == product_id.id:
                        return line.price_unit
        else:
            raise UserError('''This LC doesn't have any purchase order!''')
