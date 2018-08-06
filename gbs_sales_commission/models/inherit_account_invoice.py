from odoo import api, fields, models


class InheritAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    @api.depends('invoice_line_ids','invoice_line_ids.quantity')
    def _calculate_commission_amount(self):
        for inv in self:
            sale_order_pool = inv.env['sale.order'].search([('name', '=', inv.origin)])

            commission = None
            for sale_line in sale_order_pool.order_line:
                commission_type = sale_line.product_id.product_tmpl_id.commission_type

                if commission_type == 'fixed':
                    #loop it
                    for picking_line in sale_order_pool.picking_ids[0].pack_operation_ids:
                        commission = sale_line.commission_rate * picking_line.qty_done

                elif commission_type == 'percentage':
                    commission_percentage_amt = (sale_line.commission_rate * sale_line.price_subtotal) / 100
                    for picking_line in sale_order_pool.picking_ids[0].pack_operation_ids:
                        commission = commission_percentage_amt * picking_line.qty_done

                inv.generated_commission_amount = commission

    is_commission_generated = fields.Boolean(string='Commission Generated', default=False)
    generated_commission_amount = fields.Float(string='Commission Amount', store = True, compute='_calculate_commission_amount',)

    @api.multi
    @api.onchange('invoice_line_ids')
    def _on_change_price_unit1(self):
        for inv in self:
            sale_order_pool = inv.env['sale.order'].search([('name', '=', inv.origin)])

            commission = None
            for sale_line in sale_order_pool.order_line:
                commission_type = sale_line.product_id.product_tmpl_id.commission_type

                if commission_type == 'percentage':
                    commission_percentage_amt = (sale_line.commission_rate * inv.invoice_line_ids.price_subtotal) / 100
                    commission_per_qty = commission_percentage_amt / sale_line.product_uom_qty
                    commission = commission_per_qty * inv.invoice_line_ids.quantity

                    inv.generated_commission_amount = commission
