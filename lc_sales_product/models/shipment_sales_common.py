from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ShipmentCommon(models.Model):

    _inherit = 'purchase.shipment'

    invoice_id = fields.Many2one("account.invoice", string='Invoice Number')
    invoice_ids = fields.Many2many("account.invoice", 'lc_shipment_invoice_rel', 'shipment_id', 'invoice_id', string='Invoice Numbers')
    invoice_qty = fields.Float(string='Invoice Qty')
    to_sales_date = fields.Date('Dispatch to Sales', track_visibility='onchange')
    to_first_acceptance_date = fields.Date('1st Acceptance Date', track_visibility='onchange')
    to_second_acceptance_date = fields.Date('2nd Acceptance Date', track_visibility='onchange')
    to_buyer_date = fields.Date('Dispatch to Party', track_visibility='onchange')
    to_seller_bank_date = fields.Date('Seller Bank Receive', track_visibility='onchange')
    to_buyer_bank_date = fields.Date('Buyer Bank Receive', track_visibility='onchange')
    to_maturity_date = fields.Date('Maturity Date', track_visibility='onchange')
    bill_id = fields.Char('Bill ID', track_visibility='onchange')
    freight = fields.Char('Freight')
    goods_condition = fields.Text('Goods Condition')
    doc_preparation_date = fields.Date('Doc. Preparation Date', track_visibility='onchange')

    # Existing state override
    state = fields.Selection(
        [('draft', "Draft"),
         ('on_board', "Shipment On Board"),
         ('receive_doc', "Transfer Doc"),
         ('send_to_cnf', "Send TO C&F"),
         ('eta', "ETA"),
         ('cnf_quotation', "C&F Quotation"),
         ('approve_cnf_quotation', "Approve"),
         ('cnf_clear', "C&F Clear"),
         ('gate_in', "Gate In"),
         ('add_invoice', "Invoice"),
         ('to_sales',"To Sales"),
         ('to_buyer',"To Buyer"),
         ('to_first_acceptance',"1st Accept"),
         ('to_seller_bank',"To Seller Bank"),
         ('to_buyer_bank',"To Buyer Bank"),
         ('to_bill_id', "To Bill ID"),
         ('to_second_acceptance',"2nd Accept"),
         ('to_maturity', "To Maturity"),
         ('done', "Done"),
         ('cancel', "Cancel")], default='draft', track_visibility='onchange')


    @api.multi
    def action_draft_local_sales(self):
        lc_state = self.lc_id.state
        if lc_state == 'done' or lc_state == 'cancel':
            raise ValidationError(
                _("This LC already in " + lc_state.capitalize() + ". Before 'Reset To Draft', Need to Active This LC"))

        for obj in self.shipment_product_lines:
            if self.state != 'cancel':
                lc_product_line = self.env['lc.product.line'].search([('sale_order_id', '=', obj.sale_order_id.id), ('lc_id', '=', self.lc_id.id)])
                if lc_product_line:
                    lc_product_line.write({'product_received_qty': lc_product_line.product_received_qty-obj.product_qty})
            obj.unlink()

        self.sudo().update({'state': 'draft', 'invoice_ids': [(6, 0, [])], 'invoice_value': 0})

    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        self.invoice_value = None
        if self.invoice_id:
            self.invoice_value = self.invoice_id.amount_total

    @api.multi
    def purchase_shipment_m2o_to_m2m(self):
        for rec in self.search([('invoice_id', '!=', False)]):  # Search all the records that have value in m2o field
            rec.write({'invoice_ids': [(6, 0, [rec.invoice_id.id])]})  # Move data
