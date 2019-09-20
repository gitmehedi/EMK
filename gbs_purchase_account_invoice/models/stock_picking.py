from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        if res:
            if self.receive_type == 'lc' and self.location_dest_id.name == 'Input':
                for record in self.move_lines:
                    recv_qty = record.product_qty
                    po_line_objs = {po_obj.order_line.filtered(lambda x: x.product_id.id == record.product_id.id) for po_obj in self.shipment_id.lc_id.po_ids}
                    for po_line_obj in po_line_objs:
                        if po_line_obj:
                            if recv_qty > po_line_obj.product_qty:
                                po_line_obj.write({'qty_received': po_line_obj.qty_received + po_line_obj.product_qty})
                            else:
                                po_line_obj.write({'qty_received': po_line_obj.qty_received + recv_qty})
                            recv_qty = recv_qty - po_line_obj.product_qty
        return res