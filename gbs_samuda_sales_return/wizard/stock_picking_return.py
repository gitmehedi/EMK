# imports of odoo
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    available_qty = fields.Float("Available Quantity", digits=dp.get_precision('Product Unit of Measure'))


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _get_default_price_unit(self):
        price_unit = 0
        if 'active_id' in self.env.context:
            picking = self.env['stock.picking'].browse(self.env.context['active_id'])
            amount = sum(line.credit for line in picking.cogs_move_id.line_ids)
            price_unit = amount / picking.pack_operation_product_ids[0].qty_done

        return price_unit

    price_unit = fields.Float(string='COGS Unit Price', digits=dp.get_precision('Product Price'),
                              default=_get_default_price_unit)

    return_date = fields.Date(string='Return Date', default=datetime.today())
    return_reason = fields.Text(string='Return Reason', limit=20)

    @api.constrains('product_return_moves')
    def _check_quantity(self):
        if any(move.quantity < 0 for move in self.product_return_moves):
            raise ValidationError(_("Quantity cannot be negative"))
        if any(move.quantity > move.available_qty for move in self.product_return_moves):
            raise ValidationError(_("Quantity cannot be more than available quantity"))

    @api.model
    def default_get(self, fields):
        res = super(ReturnPicking, self).default_get(fields)

        if 'product_return_moves' in res:

            picking = self.env['stock.picking'].browse(self.env.context['active_id'])
            picking_returns = self.env['stock.picking'].search([
                ('origin', '=', picking.name),
                ('picking_type_id.code', '=', picking.picking_type_id.return_picking_type_id.code)])

            for move in res['product_return_moves']:
                # delivered qty
                qty_delivered = sum(picking.pack_operation_product_ids.filtered(
                    lambda operation: operation.product_id.id == move[2]['product_id']
                ).mapped('qty_done'))

                # returned qty of this DC
                qty_returned = sum(picking_returns.mapped('pack_operation_product_ids').filtered(
                    lambda operation: operation.product_id.id == move[2]['product_id']
                ).mapped('qty_done')) or 0.0

                # available qty for returning
                qty_available = qty_delivered - qty_returned

                if qty_available < move[2]['quantity']:
                    move[2]['quantity'] = qty_available

                move[2]['to_refund_so'] = True
                move[2]['available_qty'] = move[2]['quantity']

        return res

    @api.multi
    def _create_returns(self):
        picking = self.env['stock.picking'].browse(self.env.context['active_id'])

        pickings = self.env['stock.picking'].search([('origin', '=', picking.origin),
                                                     ('picking_type_id', '=', picking.picking_type_id.id),
                                                     ('state', 'in', ['partially_available', 'assigned'])])
        if pickings:
            raise UserError(
                _("Unreserve the DC of %s which is in 'Partially Avaliable' or 'Available' state") % picking.origin)

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

    ################# NEW Implementation #################


    def do_operation(self, rec, picking, return_moves):
        new_picking_id, pick_type_id = rec._create_returns()
        print('new_picking_id', new_picking_id)
        print('pick_type_id', pick_type_id)
        partner_acc_rec = picking.partner_id.property_account_receivable_id.id
        sale_journal_id = self.env['account.journal'].search([('type', '=', 'sale'),
                                                              ('company_id', '=', picking.company_id.id)])[0]
        sale_order_obj = self.env['sale.order'].search([('name', '=', picking.origin)])[0]
        refund_obj = {
            'number': self.env['ir.sequence'].sudo().next_by_code('account.invoice'),
            'name': rec.return_reason,
            'partner_id': picking.partner_id.id,
            'date_invoice': rec.return_date,
            'currency_id': sale_order_obj.currency_id.id,
            'sale_type_id': sale_order_obj.type_id.id,
            'type': 'out_refund',
            'user_id': self.env.user.id,
            'operating_unit_id': picking.operating_unit_id.id,
            'journal_id': sale_journal_id.id,
            'company_id': picking.company_id.id,
            'account_id': partner_acc_rec
        }
        invoice_obj = self.env['account.invoice'].create(refund_obj)
        for move in return_moves:
            invoice_line = {
                'product_id': move.product_id.id,
                'name': move.product_id.name,
                'account_id': move.product_id.property_account_income_id.id,
                'quantity': move.product_qty,
                'uom_id': move.product_id.uom_id.id,
                'price_unit': rec.price_unit,
                'invoice_id': invoice_obj.id
            }
            invoice_line_obj = self.env['account.invoice.line'].create(invoice_line)
        new_picking_id.write({'invoice_ids': [(4, invoice_obj.id)]})
        print('invoice_obj', invoice_obj)

    @api.multi
    def create_return_obj(self):
        for rec in self:
            picking = self.env['stock.picking'].browse(self.env.context['active_id'])

            if not picking.origin:
                raise UserError(
                    _("Source Document not found for this picking! \n Source Document contains the reference of sale order!"))

            if not picking.partner_id.property_account_receivable_id:
                raise UserError(_("Receivable account not found for this customer!"))
            # if picking.cogs_move_id:
            #     print('use cogs value!')
            # else:
            #
            #     print('month close logic')
            return_moves = self.product_return_moves.mapped('move_id')

            if not picking.invoice_ids:
                raise UserError(_("Invoice not found for this DC!"))
            else:
                for inv in picking.invoice_ids:
                    if inv.state == 'draft':
                        raise UserError(_("You need to validate the invoice. Invoice needs to be in open state!"))
                    elif inv.state == 'paid':
                        raise UserError(_("Invoice is already paid\n You need to unreconcile the invoice first!"))
                    elif inv.state == 'open':
                        self.do_operation(rec, picking, return_moves)
                    else:
                        raise UserError(_("Invoice needs to be in open state!"))

            # TODO: _create_returns(self): this method functionality study
