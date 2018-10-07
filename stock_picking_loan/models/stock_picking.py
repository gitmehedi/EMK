# -*- coding: utf-8 -*-
import time
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class StockPicking(models.Model):
    _inherit = "stock.picking"

    loan_id = fields.Many2one(
        'item.loan.lending',
        string='Loan Number',domain=[('state', '=', 'approved')],
        readonly=True, states={'draft': [('readonly', False)]})

    @api.onchange('receive_type')
    def onchange_receive_type(self):
        if self.receive_type:
            self.loan_id = False
            self.challan_bill_no = False
            self.move_lines = []

    @api.onchange('loan_id')
    def _onchange_loan_id(self):
        if not self.loan_id:
            return

        date_planned = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        self.partner_id = self.loan_id.borrower_id.id or False

        product_lines = []
        for loan_pro_line in self.loan_id.item_lines.filtered(lambda o: o.state == 'approved' ):
            product_lines.append((0, 0, {
                'name': self.name,
                'origin': self.name,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'picking_type_id': self.picking_type_id.id,
                'date': date_planned,
                'date_expected': date_planned,
                'product_id': loan_pro_line.product_id.id,
                'product_uom': loan_pro_line.product_uom.id,
                'product_uom_qty': loan_pro_line.due_qty,
                'price_unit': loan_pro_line.price_unit,
                'state': self.state,
            }))

        self.move_lines = product_lines

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        if res:
            picking = self.browse(self.ids)[0]
            origin_picking_objs = self.search([('name', '=', picking.origin)],limit=1)
            if picking.transfer_type == 'loan' or picking.receive_type=='loan' or origin_picking_objs.receive_type == 'loan':
                loan_borrowing_obj = self.env['item.borrowing']
                loan_lending_obj = self.env['item.loan.lending']
                if picking.location_dest_id.name == 'Stock':
                    loan_borrowing_ids = loan_borrowing_obj.search([('name', '=', picking.origin)])
                    if loan_borrowing_ids:
                        for product_line in loan_borrowing_ids[0].item_lines:
                            moves = picking.move_lines.filtered(lambda o: o.product_id == product_line.product_id and o.state != 'cancel')
                            for move in moves:
                                product_line.write({'received_qty': product_line.received_qty + move.product_qty})
                    if self.transfer_type == 'receive':
                        loan_lending_ids = loan_lending_obj.search([('id', '=', origin_picking_objs.loan_id.id)])
                        if loan_lending_ids:
                            for product_line in loan_lending_ids[0].item_lines:
                                move = picking.move_lines.filtered(lambda o: o.product_id == product_line.product_id)
                                if picking.backorder_id:
                                    product_line.write({'received_qty': product_line.received_qty + move.product_qty})
                                    if product_line.received_qty == product_line.given_qty:
                                        product_line.write({'state': 'received'})
                                else:
                                    product_line.write({'received_qty': move.product_qty})
                                    if product_line.received_qty == product_line.given_qty:
                                        product_line.write({'state': 'received'})

                            receiveable_line_list = loan_lending_ids[0].item_lines.filtered(lambda o: o.state in ('approved'))
                            if not receiveable_line_list:
                                loan_lending_ids[0].write({'state': 'received'})

                if picking.location_dest_id.name == 'Borrowers':
                    loan_lending_ids = loan_lending_obj.search([('name', '=', picking.origin)])
                    if loan_lending_ids:
                        for product_line in loan_lending_ids[0].item_lines:
                            move = picking.move_lines.filtered(lambda o: o.product_id == product_line.product_id)
                        if picking.backorder_id:
                            product_line.write({'given_qty': product_line.given_qty + move.product_qty})
                        else:
                            product_line.write({'given_qty': move.product_qty})

                if picking.location_dest_id.name == 'Lenders':
                    loan_borrowing_ids = loan_borrowing_obj.search([('return_picking_id', '=', self.id)])
                    loan_borrowing_back_ids = loan_borrowing_obj.search([('return_picking_id', '=', self.backorder_id.id)])
                    if loan_borrowing_ids:
                        for product_line in loan_borrowing_ids[0].item_lines:
                            move = picking.move_lines.filtered(lambda o: o.product_id == product_line.product_id)
                            product_line.write({'given_qty': product_line.given_qty + move.product_qty})
                    elif loan_borrowing_back_ids:
                        for product_line in loan_borrowing_back_ids[0].item_lines:
                            move = picking.move_lines.filtered(lambda o: o.product_id == product_line.product_id)
                            product_line.write({'given_qty': product_line.given_qty + move.product_qty})

        return res