from odoo import api, fields, models
from datetime import datetime

class InvoiceExportWizard(models.TransientModel):
    _name = 'invoice.export.wizard.foreign'

    invoice_id = fields.Many2one("account.invoice", string='Invoice Number')
    invoice_value = fields.Float(string='Invoice Value', track_visibility='onchange')
    invoice_ids = fields.Many2many("account.invoice", string='Invoice Numbers', track_visibility='onchange', domain=[('state', '=', 'proforma')])
    invoice_qty = fields.Float(string='Invoice QTY')
    shipment_id = fields.Many2one('purchase.shipment', default=lambda self: self.env.context.get('active_id'))

    feright_value = fields.Float(string='Freight Value')
    fob_value= fields.Float(string='FOB Value', compute='_compute_fob_value', store=False)
    is_print_cfr = fields.Boolean(string='Is Print CFR')

    # @api.model
    # def default_get(self, fields):
    #     res = super(InvoiceExportWizard, self).default_get(fields)
    #     self._onchange_shipment_id()
    #     return res

    @api.one
    def _compute_fob_value(self):
        self.fob_value = self.feright_value

    # @api.one
    # def _compute_feright_value(self):
    #     self.feright_value = self.fob_value

    @api.multi
    def save_action(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        if shipment_obj:
            total_amount = 0.0
            total_qty = 0
            for invoice_id in self.invoice_ids:
                total_amount += invoice_id.amount_total
                for invoice_line_id in invoice_id.invoice_line_ids:
                    total_qty += invoice_line_id.quantity

            shipment_obj.update({'state': 'add_invoice',
                                'invoice_id': self.invoice_id.id,
                                'invoice_value': self.invoice_value,
                                'feright_value': self.feright_value,
                                'is_print_cfr': self.is_print_cfr,
                                'invoice_ids': self.invoice_ids,
                                'invoice_value': total_amount,
                                'invoice_qty': total_qty,
                                'doc_preparation_date': datetime.now()
                                })
            shipment_obj.message_post(subject='Added invoice and value', body='Invoice Ids: %s, qty: %s and values: %s'% ([str(x.number) for x in self.invoice_ids], str(total_qty), str(total_amount)))
            return {'type': 'ir.actions.act_window_close'}

    @api.onchange('invoice_ids')
    def _onchange_shipment_id(self):
        so_list = []
        for pi_id in self.shipment_id.lc_id.pi_ids_temp:
            sale_order = self.env['sale.order'].search([('pi_id', '=', pi_id.id)])
            so_list.append(sale_order.id)

        inv_list = []
        for so in so_list:
            account_invoices = self.env['account.invoice'].search([('so_id', '=', so), ('state', 'in', ['open', 'paid'])])
            for acc_inv in account_invoices:
                purchase_shipment = self.env['purchase.shipment'].search([('invoice_ids', 'in', acc_inv.id)])
                if not purchase_shipment:
                    inv_list.append(acc_inv.id)
        return {'domain': {'invoice_ids': [('id', 'in', inv_list)]}}



    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        self.invoice_value = None
        self.fob_value = None
        self.feright_value = None
        if self.invoice_id:
            self.invoice_value = self.invoice_id.amount_total
            self.feright_value = self.invoice_value

    @api.onchange('feright_value')
    def _onchange_feright_value(self):
        self.fob_value = None
        if self.feright_value > 0:
            self.fob_value = self.invoice_value - self.feright_value

    # @api.onchange('fob_value')
    # def _onchange_fob_value(self):
    #     self.feright_value = None
    #     if self.fob_value > 0:
    #         self.feright_value = self.invoice_value - self.fob_value

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




