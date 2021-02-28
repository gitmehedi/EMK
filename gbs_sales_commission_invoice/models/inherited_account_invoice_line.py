from odoo import fields, api, models


class InheritedAccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    commission_rate = fields.Float(string="Commission")
    currency_id = fields.Many2one('res.currency', string='Currency')

    is_commission_paid = fields.Boolean(string="Is Commission Paid?", default=False)

    def _update_commission_related_vals(self, so_obj):

        vals = {
            'commission_rate': so_obj.order_line.commission_rate,
            'currency_id': so_obj.currency_id.id,
        }

        # update this field to ensure same currency on invoice line and invoice obj
        #self.invoice_id.write({'currency_id': so_obj.currency_id.id})

        self.write(vals)

    @api.multi
    @api.depends('product_id', 'quantity')
    def _calculate_commission_amount(self):
        for inv in self:
            # check invoice type
            if inv.invoice_id.type == 'in_invoice':
                break

            sale_order_pool = inv.env['sale.order'].search([('name', '=', inv.invoice_id.origin)])

            if sale_order_pool:
                inv._update_commission_related_vals(sale_order_pool)

            commission = 0
            for sale_line in sale_order_pool.order_line:
                commission_type = sale_line.product_id.product_tmpl_id.commission_type

                if commission_type == 'fixed':
                    # loop it
                    for picking_line in sale_order_pool.picking_ids[0].pack_operation_ids:
                        commission = sale_line.commission_rate * picking_line.qty_done

                        if inv.company_id.currency_id != sale_order_pool.currency_id:
                            commission = commission * sale_order_pool.currency_id.rate

                elif commission_type == 'percentage':
                    commission_percentage_amt = (sale_line.commission_rate * sale_line.price_subtotal) / 100
                    for picking_line in sale_order_pool.picking_ids[0].pack_operation_ids:
                        commission = commission_percentage_amt * picking_line.qty_done

                        if inv.company_id.currency_id != sale_order_pool.currency_id:
                            commission = commission * sale_order_pool.currency_id.rate

            inv.commission_amount = commission

    commission_amount = fields.Float(string='Commission Amount', compute='_calculate_commission_amount', store=True)

