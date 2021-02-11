from odoo import models, fields, api,_
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
                    self.sale_id.sudo().action_invoice_create(final=True)

                else:
                    self.sale_id.order_line.sudo().write({'qty_to_invoice': stock_pack_products.qty_done})
                    self.sale_id.sudo().action_invoice_create()

            if stock_pack_products.qty_done == 0 \
                    or stock_pack_products.qty_done == stock_pack_products.product_qty:
                stock_pack_products.qty_done = stock_pack_products.product_qty

                self.sale_id.order_line.sudo().write({'qty_to_invoice': stock_pack_products.qty_done})

                for do_invoices in sale_adv_pay_inv:
                    do_invoices.advance_payment_method = 'all'
                    self.sale_id.sudo().action_invoice_create(final=True)
                    break
            else:
                self.sale_id.order_line.sudo().write({'qty_to_invoice': stock_pack_products.qty_done})
                for do_invoices in sale_adv_pay_inv:
                    do_invoices.advance_payment_method = 'delivered'
                    self.sale_id.sudo().action_invoice_create()
                    break

    def update_invoice_for_picking_return(self):
        """ Update customer invoice for DC return from customer """
        if self.sale_id:
            draft_invoices = self.sale_id.invoice_ids.filtered(lambda reg: reg.state == 'draft')
            if draft_invoices:
                for stock_pack_products in self.pack_operation_product_ids:
                    pack_quantity = 0.0
                    if stock_pack_products.qty_done:
                        pack_quantity = stock_pack_products.qty_done
                    else:
                        pack_quantity = stock_pack_products.product_qty
                    for draft_invoice in draft_invoices:
                        invoice_line = draft_invoice.invoice_line_ids.filtered(lambda line: line.product_id.id == stock_pack_products.product_id.id and line.quantity >= pack_quantity)
                        if invoice_line:
                            res_invoice_line = invoice_line[0]
                            aval_qty = res_invoice_line.quantity - pack_quantity
                            res_invoice_line.sudo().write({'quantity': aval_qty})
            else:
                raise UserError(_('Unable to return the product because \
                                            there are no invoice in draft stage for this Sale Order.'))
