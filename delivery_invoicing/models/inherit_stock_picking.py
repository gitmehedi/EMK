# imports of python
import pytz
from datetime import datetime

# import of odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Picking(models.Model):
    _inherit = 'stock.picking'

    delivery_address = fields.Char('Delivery Address', compute='_get_delivery_address', readonly=False)

    @api.multi
    def _get_delivery_address(self):
        for stock in self:
            if stock.sale_id.partner_shipping_id:
                stock.delivery_address = stock.sale_id.partner_shipping_id.name
            else:
                stock.delivery_address = ''

    @api.multi
    def do_transfer(self):
        """ override do_transfer to create a customer invoice for delivery orders """
        # do default operation
        res = super(Picking, self).do_transfer()

        # check for DC
        if res and self.picking_type_id.code == 'outgoing':
            # create a customer invoice for a DC
            self.create_invoice_for_picking()

        # check for DC return from customer
        if res and self.picking_type_id.code == 'outgoing_return':
            # reduce returned qty from customer invoice
            # of which state is in draft
            self.update_invoice_for_picking_return()

        return res

    def create_invoice_for_picking(self):
        """ Create customer invoice for DC """
        sale_adv_pay_inv = self.env['sale.advance.payment.inv'].search([])

        for stock_pack_products in self.pack_operation_product_ids:
            if not sale_adv_pay_inv:
                if stock_pack_products.qty_done == 0 \
                        or stock_pack_products.qty_done == stock_pack_products.product_qty:

                    stock_pack_products.qty_done = stock_pack_products.product_qty
                    self.sale_id.order_line.sudo().write({'qty_to_invoice': stock_pack_products.qty_done})
                    new_invoice_ids = self.sale_id.sudo().action_invoice_create(final=True)
                    for inv_id in new_invoice_ids:
                        new_invoice = self.env['account.invoice'].browse(inv_id)
                        new_invoice.write({'date_invoice': self.convert_time_as_timezone(self.date_done)})

                else:
                    self.sale_id.order_line.sudo().write({'qty_to_invoice': stock_pack_products.qty_done})
                    new_invoice_ids = self.sale_id.sudo().action_invoice_create()
                    for inv_id in new_invoice_ids:
                        new_invoice = self.env['account.invoice'].browse(inv_id)
                        new_invoice.write({'date_invoice': self.convert_time_as_timezone(self.date_done)})

            if stock_pack_products.qty_done == 0 \
                    or stock_pack_products.qty_done == stock_pack_products.product_qty:
                stock_pack_products.qty_done = stock_pack_products.product_qty

                self.sale_id.order_line.sudo().write({'qty_to_invoice': stock_pack_products.qty_done})

                for do_invoices in sale_adv_pay_inv:
                    do_invoices.advance_payment_method = 'all'
                    new_invoice_ids = self.sale_id.sudo().action_invoice_create(final=True)
                    for inv_id in new_invoice_ids:
                        new_invoice = self.env['account.invoice'].browse(inv_id)
                        new_invoice.write({'date_invoice': self.convert_time_as_timezone(self.date_done)})
                    break
            else:
                self.sale_id.order_line.sudo().write({'qty_to_invoice': stock_pack_products.qty_done})
                for do_invoices in sale_adv_pay_inv:
                    do_invoices.advance_payment_method = 'delivered'
                    new_invoice_ids = self.sale_id.sudo().action_invoice_create()
                    for inv_id in new_invoice_ids:
                        new_invoice = self.env['account.invoice'].browse(inv_id)
                        new_invoice.write({'date_invoice': self.convert_time_as_timezone(self.date_done)})
                    break

    # def update_invoice_for_picking_return(self):
    #     """ Update customer invoice for DC return from customer """
    #     if self.sale_id:
    #         draft_invoices = self.sale_id.invoice_ids.filtered(lambda reg: reg.state == 'draft')
    #         if draft_invoices:
    #             for stock_pack_products in self.pack_operation_product_ids:
    #                 pack_quantity = 0.0
    #                 if stock_pack_products.qty_done:
    #                     pack_quantity = stock_pack_products.qty_done
    #                 else:
    #                     pack_quantity = stock_pack_products.product_qty
    #                 for draft_invoice in draft_invoices:
    #                     invoice_line = draft_invoice.invoice_line_ids.filtered(lambda line: line.product_id.id == stock_pack_products.product_id.id and line.quantity >= pack_quantity)
    #                     if invoice_line:
    #                         res_invoice_line = invoice_line[0]
    #                         aval_qty = res_invoice_line.quantity - pack_quantity
    #                         res_invoice_line.sudo().write({'quantity': aval_qty})
    #         else:
    #             raise UserError(_('Unable to return the product because \
    #                                         there are no invoice in draft stage for this Sale Order.'))

    def update_invoice_for_picking_return(self):
        """ Update customer invoice for DC return from customer """
        # New Return Fix (Shoaib)
        # invoices = self.sale_id.invoice_ids.filtered(lambda inv: inv.state == 'open')
        pick = self.env.context.get('active_id')
        invoices = self.env['account.invoice'].sudo().search([('picking_ids', 'in', pick), ('state', '=', 'open')])

        #########[FIXED for new sales return] shoaib
        # invoices = self.sale_id.invoice_ids.filtered(lambda inv: inv.state == 'draft')
        if not invoices:
            raise UserError(
                _('Unable to return the product because invoice is not in open state!'))

        return_qty = sum(pack.qty_done or pack.product_qty for pack in self.pack_operation_product_ids)
        invoice_qty = sum(line.quantity for inv in invoices for line in inv.invoice_line_ids)

        if return_qty > invoice_qty:
            raise UserError(_('Unable to return the product because return quantity is greater than invoice quantity.'))

        for pack in self.pack_operation_product_ids:
            is_deduct = False
            pack_qty = pack.qty_done or pack.product_qty
            for inv in invoices:
                line = inv.invoice_line_ids.filtered(
                    lambda line: line.product_id.id == pack.product_id.id and line.quantity >= pack_qty)
                if line:
                    qty = line.quantity - return_qty
                    line.sudo().write({'quantity': qty})
                    is_deduct = True
                    break

            if not is_deduct:
                for inv in invoices:
                    if pack_qty > 0:
                        line = inv.invoice_line_ids.filtered(lambda line: line.product_id.id == pack.product_id.id)
                        qty = line.quantity - pack_qty
                        pack_qty = pack_qty - line.quantity
                        line.sudo().write({'quantity': qty if qty > 0 else 0})

    def convert_time_as_timezone(self, datetime_str):
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        dt = datetime.strftime(
            pytz.utc.localize(datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")).astimezone(local),
            "%Y-%m-%d %H:%M:%S")
        return dt
