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
    def do_new_transfer(self):
        res = super(Picking, self).do_new_transfer()

        if self.location_dest_id.name == 'Customers':
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
                        break;
                else:
                    self.sale_id.order_line.sudo().write({'qty_to_invoice': stock_pack_products.qty_done})
                    for do_invoices in sale_adv_pay_inv:
                        do_invoices.advance_payment_method = 'delivered'
                        self.sale_id.sudo().action_invoice_create()
                        break;

        if self.location_dest_id.name =='Stock' and self.sale_id:
            draft_invoices = self.sale_id.invoice_ids.filtered(lambda reg: reg.state == 'draft')
            if draft_invoices:
                for stock_pack_products in self.pack_operation_product_ids:
                    pack_quantity = 0.0
                    if stock_pack_products.qty_done:
                        pack_quantity = stock_pack_products.qty_done
                    else:
                        pack_quantity = stock_pack_products.product_qty
                    for draft_invoice in draft_invoices:
                        invoice_line = draft_invoice.invoice_line_ids.filtered(lambda line: line.product_id.id ==stock_pack_products.product_id.id and line.quantity >= pack_quantity)
                        if invoice_line:
                            res_invoice_line = invoice_line[0]
                            aval_qty = res_invoice_line.quantity - pack_quantity
                            res_invoice_line.sudo().write({'quantity': aval_qty})
            else:
                raise UserError(_('Unable to return the product because \
                                    there are no invoice in draft stage for this Sale Order.'))
            #     for stock_pack_products in self.pack_operation_product_ids:
            #         pack_quantity = 0.0
            #         if stock_pack_products.qty_done:
            #             pack_quantity = stock_pack_products.qty_done
            #         else:
            #             pack_quantity = stock_pack_products.product_qty
            #         if pack_quantity:
            #             so_line = self.sale_id.order_line.filtered(lambda line: line.product_id.id ==stock_pack_products.product_id.id)
            #             so_line.write({'qty_to_invoice': -pack_quantity})
            #     self.sale_id.sudo().action_invoice_create(final=True)

        return res