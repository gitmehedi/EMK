from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('sale_type_id')
    def onchange_sale_type_id(self):
        if self.sale_type_id:
            product_acc_list = self.env['sale.type.product.account'].search(
                [('product_id', '=', [i.product_id.id for i in self.invoice_line_ids]),
                 ('sale_order_type_id', '=', self.sale_type_id.id)])

            for inv_line in self.invoice_line_ids:
                if product_acc_list:
                    for sale_acc_line in product_acc_list:
                        if sale_acc_line.sale_order_type_id.id == self.sale_type_id.id and inv_line.product_id.id == sale_acc_line.product_id.id:
                                inv_line.account_id = sale_acc_line.account_id.id




class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.onchange('product_id')
    def onchange_sale_type_id(self):
        if self.product_id:
            product_account = self.env['sale.type.product.account'].search(
                [('product_id', '=', self.product_id.id),
                 ('sale_order_type_id', '=', self.invoice_id.sale_type_id.id)])
            if self.invoice_id.sale_type_id:
                if product_account:
                    self.account_id = product_account.account_id.id



class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_new_transfer(self):
        res = super(Picking, self).do_new_transfer()
        product_acc_list = self.env['sale.type.product.account'].search(
            [('product_id', '=', self.sale_id.product_id.id)])

        for inv in self.sale_id.invoice_ids:
            for inv_line in inv.invoice_line_ids:
                if product_acc_list:
                    for sale_acc_line in product_acc_list:
                        if sale_acc_line.sale_order_type_id.id == self.sale_id.type_id.id and inv_line.product_id.id == sale_acc_line.product_id.id:
                            inv_line.account_id = sale_acc_line.account_id.id

        return res

