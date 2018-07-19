from odoo import models, fields, api


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


        return res