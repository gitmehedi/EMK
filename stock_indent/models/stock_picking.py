from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        if res:
            picking = self.browse(self.ids)[0]
            indent_obj = self.env['indent.indent']
            indent_ids = indent_obj.search([('name', '=', picking.origin)])
            if indent_ids:
                for product_line in indent_ids[0].product_lines:
                    move = picking.move_lines.filtered(lambda o: o.product_id == product_line.product_id)
                    if picking.backorder_id:
                        product_line.write({'received_qty': product_line.received_qty + move.product_qty})
                    else:
                        product_line.write({'received_qty': move.product_qty})
                picking_ids = self.search([('origin', '=', picking.origin)])
                flag = True
                # for picking in self.browse(self.ids):
                for picking in picking_ids:
                    if picking.state not in ('done', 'cancel'):
                        flag = False
                if flag:
                    indent_ids.write({'state': 'received'})

        return res

    @api.multi
    def _create_backorder(self, backorder_moves=[]):
        res = super(StockPicking, self)._create_backorder(backorder_moves)

        # res: list of backorder pickings
        # unreserved the reserve qty of backorder pickings
        for backorder_picking in res.filtered(
                lambda x: x.picking_type_id.code == 'internal' and x.origin.find('Indent-') != -1):
            if backorder_picking.quant_reserved_exist and (
                    backorder_picking.state in ['draft', 'partially_available', 'assigned']):
                backorder_picking.do_unreserve()

        return res
