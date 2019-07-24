from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    so_id = fields.Many2one('sale.order', string='SO No', readonly=True)

    @api.onchange('sale_type_id')
    def onchange_sale_type_id(self):
        if self.sale_type_id:
            product_acc_list = self.env['sale.type.product.account'].search(
                [('product_id', '=', [i.product_id.id for i in self.invoice_line_ids]),
                 ('sale_order_type_id', '=', self.sale_type_id.id)])

            if product_acc_list:
                for inv_line in self.invoice_line_ids:
                    for sale_acc_line in product_acc_list:
                        if sale_acc_line.sale_order_type_id.id == self.sale_type_id.id and inv_line.product_id.id == sale_acc_line.product_id.id:
                            if not sale_acc_line.packing_mode_id:
                                inv_line.account_id = sale_acc_line.account_id.id
                            else:
                                so_obj = self.env['sale.order'].search([('name', '=', self.origin)])
                                if so_obj.pack_type == sale_acc_line.packing_mode_id:
                                    inv_line.account_id = sale_acc_line.account_id.id
                                    break;


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.onchange('product_id')
    def onchange_sale_type_id(self):
        if self.product_id:
            product_account = self.env['sale.type.product.account'].search(
                [('product_id', '=', self.product_id.id),
                 ('sale_order_type_id', '=', self.invoice_id.sale_type_id.id)])

            if product_account:
                for sale_acc_line in product_account:
                    if self.invoice_id.sale_type_id:
                        if not sale_acc_line.packing_mode_id:
                            self.account_id = sale_acc_line.account_id.id
                        else:
                            so_obj = self.env['sale.order'].search([('name', '=', self.invoice_id.origin)])
                            if so_obj.pack_type == sale_acc_line.packing_mode_id:
                                self.account_id = sale_acc_line.account_id.id
                                break;


class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_new_transfer(self):
        res = super(Picking, self).do_new_transfer()
        product_acc_list = self.env['sale.type.product.account'].search(
            [('product_id', '=', self.sale_id.product_id.id)])

        if product_acc_list:
            for inv in self.sale_id.invoice_ids:

                # Set so_id for getting reference SO-> LC
                inv.so_id = self.sale_id
                for inv_line in inv.invoice_line_ids:
                    for sale_acc_line in product_acc_list:
                        if sale_acc_line.sale_order_type_id.id == self.sale_id.type_id.id and inv_line.product_id.id == sale_acc_line.product_id.id:
                            if not sale_acc_line.packing_mode_id:
                                inv_line.account_id = sale_acc_line.account_id.id
                            else:
                                so_obj = self.env['sale.order'].search([('name', '=', self.origin)])
                                if so_obj.pack_type == sale_acc_line.packing_mode_id:
                                    inv_line.account_id = sale_acc_line.account_id.id
                                    break;

        return res
