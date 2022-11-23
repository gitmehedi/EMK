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

        index = 0
        for obj in self.shipment_product_lines:
            if self.state != 'cancel':
                if obj.sale_order_id:
                    lc_product_line = self.env['lc.product.line'].search([('sale_order_id', '=', obj.sale_order_id.id), ('lc_id', '=', self.lc_id.id)])
                    if len(lc_product_line) == 1:
                        lc_product_line.write({'product_received_qty': lc_product_line.product_received_qty-obj.product_qty})
                    else:
                        for prod_line in lc_product_line:
                            reset_qty = prod_line.product_received_qty - obj.product_qty

                            if reset_qty >= 0:
                                prod_line.write({'product_received_qty': reset_qty})
                            else:
                                for p_line in lc_product_line:
                                    reset_qty = p_line.product_received_qty - obj.product_qty
                                    if reset_qty >= 0:
                                        p_line.write({'product_received_qty': reset_qty})
                    obj.unlink()
                else:
                    lc_product_line_list = self.env['lc.product.line'].search([('lc_id', '=', self.lc_id.id), ('product_id', '=', obj.product_id.id)])
                    if len(lc_product_line_list) > 1:
                        lc_product_line = lc_product_line_list[index]
                        if lc_product_line.product_received_qty == 0:
                            for lc_prod_line in lc_product_line_list:
                                if lc_prod_line.product_received_qty != 0:
                                    lc_product_line = lc_prod_line
                                    break
                            lc_product_line.write({'product_received_qty': lc_product_line.product_received_qty - obj.product_qty})

                        elif lc_product_line.product_received_qty - obj.product_qty < 0:
                            diff_qty = obj.product_qty - lc_product_line.product_received_qty
                            lc_product_line.write({'product_received_qty': 0})
                            for lc_prod_line in lc_product_line_list:
                                if lc_prod_line.product_received_qty > diff_qty:
                                    lc_prod_line.write({'product_received_qty': lc_prod_line.product_received_qty - diff_qty})
                                    break
                        else:
                            lc_product_line.write({'product_received_qty': 0})
                    else:
                        lc_product_line_list.write({'product_received_qty': lc_product_line_list.product_received_qty - obj.product_qty})
                obj.unlink()

        self.reset_shipment()
        self.sudo().update({'state': 'draft', 'invoice_ids': [(6, 0, [])], 'invoice_value': 0})

    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        self.invoice_value = None
        if self.invoice_id:
            self.invoice_value = self.invoice_id.amount_total

    def reset_shipment(self):
        self.to_sales_date = False
        self.to_buyer_date = False
        self.to_first_acceptance_date = False
        self.to_seller_bank_date = False
        self.to_buyer_bank_date = False
        self.bill_id = False
        self.to_second_acceptance_date = False
        self.to_maturity_date = False
        self.shipment_done_date = False
        self.ait_amount = False
        self.payment_rec_date = False
        self.payment_rec_amount = False
        self.discrepancy_amount = False
        self.payment_charge = False
        self.invoice_value = False
        self.doc_preparation_date = False
        self.transport_by = False
        self.vehical_no = False
        self.freight = False
        self.gross_weight = False
        self.net_weight = False
        self.count_qty = False
        self.count_uom = False
        self.weight_uom = False
        self.bl_date = False
        self.truck_receipt_no = False
        self.truck_receipt_no = False
        self.container_no = False
        self.freight_Value = False
        self.fob_value = False
        self.invoice_number_dummy = False
        self.invoice_date_dummy = False
        self.comment = False

    @api.multi
    def purchase_shipment_m2o_to_m2m(self):
        for rec in self.search([('invoice_id', '!=', False)]):  # Search all the records that have value in m2o field
            rec.write({'invoice_ids': [(6, 0, [rec.invoice_id.id])]})  # Move data
