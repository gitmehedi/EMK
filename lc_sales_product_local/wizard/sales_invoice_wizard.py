from odoo import api, fields, models


class InvoiceExportWizard(models.TransientModel):
    _name = 'invoice.export.wizard'

    invoice_id = fields.Many2one("account.invoice", string='Invoice Number')
    invoice_ids = fields.Many2many("account.invoice", string='Invoice Numbers')
    invoice_qty = fields.Float(string='Invoice QTY')
    invoice_value = fields.Float(string='Invoice Value')

    shipment_id = fields.Many2one('purchase.shipment', default=lambda self: self.env.context.get('active_id'))

    @api.multi
    def save_action(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        if shipment_obj:
            total_amount = 0
            total_qty = 0
            for invoice_id in self.invoice_ids:
                total_amount += invoice_id.amount_total
                for invoice_line_id in invoice_id.invoice_line_ids:
                    total_qty += invoice_line_id.quantity

            # shipment_obj.write({'state': 'add_invoice', 'invoice_id': self.invoice_id.id,
            #                     'invoice_value': self.invoice_value
            #                     })
            shipment_obj.update({
                'state': 'add_invoice',
                'invoice_ids': self.invoice_ids,
                'invoice_value': total_amount,
                'invoice_qty': total_qty,
            })
            return {'type': 'ir.actions.act_window_close'}

    # @api.onchange('shipment_id')
    # def _onchange_shipment_id(self):
    #     invoice_ids = self.env['account.invoice'].search(
    #         ['&', '|', ('partner_id', '=', self.shipment_id.lc_id.second_party_applicant.id),
    #          ('partner_id', 'in', self.shipment_id.lc_id.second_party_applicant.child_ids.ids), '&',
    #          ('sale_type_id.sale_order_type', 'in', ['lc_sales', 'tt_sales', 'contract_sales']),
    #          ('state', 'in', ['open', 'paid'])])
    #
    #     used_invoice_ids = self.env['purchase.shipment'].search([('invoice_id', 'in', invoice_ids.ids)]).mapped('invoice_id')
    #     domain_id_list = list(set(invoice_ids.ids) - set(used_invoice_ids.ids))
    #
    #     return {'domain': {'invoice_id': [('id', 'in', domain_id_list)]}}

    @api.onchange('shipment_id')
    def _onchange_shipment_id(self):
        so_list = []
        for pi_id in self.shipment_id.lc_id.pi_ids_temp:
            sale_order = self.env['sale.order'].search([('pi_id', '=', pi_id.id)])
            so_list.append(sale_order.id)

        inv_list = []
        for so in so_list:
            account_invoices = self.env['account.invoice'].search(
                [('so_id', '=', so), ('state', 'in', ['open', 'paid'])])
            for acc_inv in account_invoices:
                purchase_shipment = self.env['purchase.shipment'].search([('invoice_ids', 'in', acc_inv.id)])
                if not purchase_shipment:
                    inv_list.append(acc_inv.id)
        return {'domain': {'invoice_ids': [('id', 'in', inv_list)]}}

    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        self.invoice_value = None
        if self.invoice_id:
            self.invoice_value = self.invoice_id.amount_total

    @api.onchange('invoice_ids')
    def _onchange_invoice_ids(self):
        self.invoice_value = None
        total_amount = 0
        total_qty = 0
        for invoice_id in self.invoice_ids:
            total_amount += invoice_id.amount_total
            for invoice_line_id in invoice_id.invoice_line_ids:
                total_qty += invoice_line_id.quantity
        self.invoice_value = total_amount
        self.invoice_qty = total_qty






