from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    deduct_commission = fields.Boolean(
        default=True,
        help='Deduct commission amount equivalent with returned quantity'
    )
    deduct_refund = fields.Boolean(
        default=True,
        help='Deduct refund amount equivalent with returned quantity'
    )

    @api.multi
    def create_return_obj(self):
        picking = self.env['stock.picking'].browse(self.env.context['active_id'])
        invoice_ids = self.env['account.invoice'].sudo().search([('picking_ids', '=', picking.id)])
        so_ids = self.env['sale.order'].search([('name', '=', picking.origin)])[0]

        purchase_order_ids = self.env['purchase.order'].sudo().search([('sale_order_ids', 'in', so_ids.ids)])
        for po in purchase_order_ids:
            if po.invoice_ids and (po.is_commission_claim or po.is_refund_claim):
                # if one or more bill state is not cancel.
                bill_available = any([bill.state != 'cancel' for bill in po.invoice_ids])
                if bill_available:
                    raise UserError(_("Can't return.\nReason: Commission/Refund already claimed. "))

        for so in so_ids:
            so.deduct_commission = self.deduct_commission
            so.deduct_refund = self.deduct_refund

        # reverse commission/refund journal entry

        return_moves_ = self.product_return_moves.mapped('move_id')
        pro_returns_ = self.product_return_moves

        for move_ in return_moves_:
            returned_qty_ = 0
            for _rtn in pro_returns_:
                if _rtn.move_id.id == move_.id:
                    returned_qty_ = _rtn.quantity

            for inv in invoice_ids:
                commission_move = inv.commission_move_id
                if self.deduct_commission and not commission_move:
                    raise UserError(_("Deduction not possible because commission move not found for this invoice."))

                if self.deduct_commission and commission_move:
                    ref = "reversal of: " + commission_move.name
                    move_of_reverse_ = commission_move.copy(default={'ref': ref, 'date': self.return_date})
                    for aml in move_of_reverse_.line_ids:
                        aml.date = self.return_date
                        aml.date_maturity = self.return_date
                        if inv.invoice_line_ids[0].quantity > 0:
                            if aml.debit > 0:
                                reverse_debit = (aml.debit / inv.invoice_line_ids[0].quantity) * returned_qty_
                                aml.name = "(debit= " + str(aml.debit) + "/ invoice quantity= " + str(
                                    inv.invoice_line_ids[0].quantity) + ")" + "* returned quantity= " + str(
                                    returned_qty_)
                                aml.debit = 0
                                aml.credit = reverse_debit
                            else:
                                reverse_credit = (aml.credit / inv.invoice_line_ids[0].quantity) * returned_qty_
                                aml.name = "(credit= " + str(aml.credit) + "/ invoice quantity= " + str(
                                    inv.invoice_line_ids[0].quantity) + ")" + "* returned quantity= " + str(
                                    returned_qty_)
                                aml.credit = 0
                                aml.debit = reverse_credit
                    move_of_reverse_.post()
                    inv.sudo().write({'reverse_commission_move_id': move_of_reverse_.id})

                refund_move = inv.refund_move_id
                if self.deduct_refund and not refund_move:
                    raise UserError(_("Deduction not possible because refund move not found for this invoice."))

                if self.deduct_refund and refund_move:
                    ref = "reversal of: " + refund_move.name
                    refund_move_of_reverse_ = refund_move.copy(default={'ref': ref, 'date': self.return_date})
                    for aml in refund_move_of_reverse_.line_ids:
                        aml.date = self.return_date
                        aml.date_maturity = self.return_date
                        if inv.invoice_line_ids[0].quantity > 0:
                            if aml.debit > 0:
                                reverse_debit = (aml.debit / inv.invoice_line_ids[0].quantity) * returned_qty_
                                aml.name = "(debit= " + str(aml.debit) + "/ invoice quantity= " + str(
                                    inv.invoice_line_ids[0].quantity) + ")" + "* returned quantity= " + str(
                                    returned_qty_)
                                aml.debit = 0
                                aml.credit = reverse_debit
                            else:
                                reverse_credit = (aml.credit / inv.invoice_line_ids[0].quantity) * returned_qty_
                                aml.name = "(credit= " + str(aml.credit) + "/ invoice quantity= " + str(
                                    inv.invoice_line_ids[0].quantity) + ")" + "* returned quantity= " + str(
                                    returned_qty_)
                                aml.credit = 0
                                aml.debit = reverse_credit
                    refund_move_of_reverse_.post()
                    inv.sudo().write({'reverse_refund_move_id': refund_move_of_reverse_.id})

        return super(ReturnPicking, self).create_return_obj()
