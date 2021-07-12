# imports of odoo
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _get_default_price_unit(self):
        picking = self.env['stock.picking'].browse(self.env.context['active_id'])
        amount = sum(line.credit for line in picking.cogs_move_id.line_ids)
        price_unit = amount / picking.pack_operation_product_ids[0].qty_done
    
        return price_unit

    price_unit = fields.Float(string='COGS Unit Price', digits=dp.get_precision('Product Price'), default=_get_default_price_unit)

    @api.constrains('product_return_moves')
    def _check_quantity(self):
        if any(move.quantity < 0 for move in self.product_return_moves):
            raise ValidationError(_("Quantity cannot be negative"))

    @api.model
    def default_get(self, fields):
        res = super(ReturnPicking, self).default_get(fields)

        if 'product_return_moves' in res:
            for move in res['product_return_moves']:
                move[2]['to_refund_so'] = True

        return res

    @api.multi
    def _create_returns(self):
        picking = self.env['stock.picking'].browse(self.env.context['active_id'])

        pickings = self.env['stock.picking'].search([('origin', '=', picking.origin),
                                                    ('picking_type_id', '=', picking.picking_type_id.id),
                                                    ('state', 'in', ['partially_available', 'assigned'])])
        if pickings:
            raise UserError(_("Unreserve the DC of %s which is in 'Partially Avaliable' or 'Available' state") % picking.origin)

        new_picking_id, picking_type_id = super(ReturnPicking, self)._create_returns()

        new_picking = self.env['stock.picking'].browse(new_picking_id)

        if new_picking.picking_type_id.code == 'outgoing_return':

            for pack in new_picking.pack_operation_ids:
                if pack.product_qty > 0:
                    pack.write({'qty_done': pack.product_qty})

            new_picking.write({'date_done': picking.date_done})

            new_picking.do_transfer()
            new_picking.button_ac_approve()
            new_picking.button_approve()

            # reverse cogs entry
            move = self.env['account.move'].search([('id', '=', picking.cogs_move_id.id)])
            if move:
                self.do_cogs_reverse_accounting(new_picking, move)

            # Create DC with return qty or Add return qty with existing DC
            existing_dc = self.env['stock.picking'].search([('origin', '=', picking.origin),
                                                         ('picking_type_id', '=', picking.picking_type_id.id),
                                                         ('state', '=', 'confirmed')])
            if existing_dc:
                existing_dc.move_lines[0].product_uom_qty += new_picking.pack_operation_product_ids[0].qty_done
            else:
                new_dc = picking.copy()
                new_dc.move_lines[0].product_uom_qty = new_picking.pack_operation_product_ids[0].qty_done
                new_dc.action_confirm()

        return new_picking_id, picking_type_id

    def do_cogs_reverse_accounting(self, picking, move):
        product = picking.pack_operation_product_ids[0].product_id
        stock_pack_operation = picking.pack_operation_product_ids[0]

        ref = "reversal of: " + move.name
        amount = self.price_unit * stock_pack_operation.qty_done
        name = product.display_name + "; Rate: " + str(self.price_unit) + "; Qty: " + str(stock_pack_operation.qty_done)

        move_of_reverse_cogs = move.copy(default={'ref': ref})
        for aml in move_of_reverse_cogs.line_ids:
            if aml.debit > 0:
                aml.name = name
                aml.debit = 0
                aml.credit = amount
            else:
                aml.name = name
                aml.credit = 0
                aml.debit = amount

        move_of_reverse_cogs.post()
