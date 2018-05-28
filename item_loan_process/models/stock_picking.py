from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        if res:
            picking = self.browse(self.ids)[0]
            if picking.location_dest_id.name == 'Stock':
                loan_obj = self.env['item.borrowing']
                loan_ids = loan_obj.search([('name', '=', picking.origin)])
                if loan_ids:
                    for product_line in loan_ids[0].item_lines:
                        move = picking.move_lines.filtered(lambda o: o.product_id == product_line.product_id)
                        if picking.backorder_id:
                            product_line.write({'received_qty': product_line.received_qty+move.product_qty})
                        else:
                            product_line.write({'received_qty': move.product_qty})
            if picking.location_dest_id.name == 'Customers':
                loan_obj = self.env['item.loan.lending']
                loan_ids = loan_obj.search([('name', '=', picking.origin)])
                if loan_ids:
                    for product_line in loan_ids[0].item_lines:
                        move = picking.move_lines.filtered(lambda o: o.product_id == product_line.product_id)
                        if picking.backorder_id:
                            product_line.write({'given_qty': product_line.given_qty+move.product_qty})
                        else:
                            product_line.write({'given_qty': move.product_qty})

        return res