from odoo import models, fields, api


class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_new_transfer(self):
        res = super(Picking, self).do_new_transfer()

        sale_adv_pay_inv = self.env['sale.advance.payment.inv'].search([])

        for stock_pack_products in self.pack_operation_product_ids:

            if stock_pack_products.qty_done == 0 \
                    or stock_pack_products.qty_done == stock_pack_products.product_qty:
                stock_pack_products.qty_done = stock_pack_products.product_qty

                sale_order_obj = self.sale_id.order_line.write({'qty_to_invoice': stock_pack_products.qty_done})

                for do_invoices in sale_adv_pay_inv:
                        do_invoices.advance_payment_method = 'all'
                        self.sale_id.action_invoice_create(final=True)
                        break;
            else:
                sale_order_obj = self.sale_id.order_line.write({'qty_to_invoice': stock_pack_products.qty_done})
                for do_invoices in sale_adv_pay_inv:
                    do_invoices.advance_payment_method = 'delivered'
                    self.sale_id.action_invoice_create()
                    break;


        if not sale_adv_pay_inv:
            # do someting
            pass

        return res
