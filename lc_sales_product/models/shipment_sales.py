from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Shipment(models.Model):

    _inherit = 'purchase.shipment'

    invoice_id = fields.Many2one("account.invoice", string='Invoice Number')

    to_sales_date = fields.Date('Dispatch to Sales', track_visibility='onchange')
    to_buyer_date = fields.Date('Dispatch to Party', track_visibility='onchange')
    to_seller_bank_date = fields.Date('Seller Bank Receive', track_visibility='onchange')
    to_buyer_bank_date = fields.Date('Buyer Bank Receive', track_visibility='onchange')
    to_maturity_date = fields.Date('Maturity Date', track_visibility='onchange')
    bill_id = fields.Char('Bill ID', track_visibility='onchange')
    freight = fields.Char('Freight')
    goods_condition = fields.Text('Goods Condition')

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
         ('to_seller_bank',"To Seller Bank"),
         ('to_buyer_bank',"To Buyer Bank"),
         ('to_maturity', "To Maturity"),
         ('done', "Done"),
         ('cancel', "Cancel")], default='draft', track_visibility='onchange')

    # @api.onchange('lc_id')
    # def _onchange_lc_id(self):
    #     if self.lc_id:
    #
    #         # invoice_objs = self.env['account.invoice'].search([('sale_type_id.sale_order_type', '=', 'lc_sales'),
    #         #                                                ('state', 'in', ['open', 'paid']),
    #         #                                                ('id', 'not in', [i.invoice_id.id for i in self.search([])])])
    #         # domain_id = invoice_objs.search(['|',('partner_id', '=', self.lc_id.second_party_applicant.id),
    #         #                                  ('partner_id', 'in', self.lc_id.second_party_applicant.child_ids.ids)]).ids
    #
    #         invoice_objs = self.env['account.invoice'].search([('sale_type_id.sale_order_type', '=', 'lc_sales'),
    #                                                            ('state', 'in', ['open', 'paid']), ])
    #
    #         domain_id = invoice_objs.search(['&', '|', ('partner_id', '=', self.lc_id.second_party_applicant.id),
    #                                          ('partner_id', 'in', self.lc_id.second_party_applicant.child_ids.ids),
    #                                          ('id', 'not in', [i.invoice_id.id for i in self.search([])])]).ids
    #
    #         return {'domain': {'invoice_id': [('id','in',domain_id)]}}


    @api.multi
    def action_draft_local_sales(self):

        lc_state = self.lc_id.state
        if lc_state == 'done' or lc_state == 'cancel':
            raise ValidationError(_("This LC already in "+ lc_state.capitalize()  +". Before 'Reset To Draft', Need to Active This LC"))

        if self.shipment_product_lines:
            for obj in self.shipment_product_lines:
                lc_product_line = self.env['lc.product.line'].search([('lc_id', '=', self.lc_id.id),
                                                                      ('product_id', '=', obj.product_id.id)])

                if len(lc_product_line) > 1:
                    # raise ValidationError(("Unable to update due to multiple same product."))
                    # break
                    res_wizard_view = self.env.ref('lc_sales_product.reset_lc_wizard_view')
                    res = {
                        'name': _('Please Select LC Product to return document qty for reset'),
                        'view_type': 'form',
                        'view_mode': 'form',
                        'view_id': res_wizard_view and res_wizard_view.id or False,
                        'res_model': 'reset.lc.wizard',
                        'type': 'ir.actions.act_window',
                        'nodestroy': True,
                        'target': 'new',
                    }
                    return res
                else:
                    lc_product_line.write({'product_received_qty': lc_product_line.product_received_qty-obj.product_qty})

            self.shipment_product_lines.unlink()

        self.write({'state': 'draft'})

    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        self.invoice_value = None
        if self.invoice_id:
            self.invoice_value = self.invoice_id.amount_total

    @api.multi
    def action_doc_receive_export(self):
        res = self.env.ref('lc_sales_product.doc_receive_wizard_export')
        result = {
            'name': _('Please Enter Shipment Products'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'doc.receive.wizard.export',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    @api.multi
    def action_view_shipment_export(self):

        res = self.env.ref('lc_sales_product.view_shipment_export_form')

        result = {'name': _('Shipment'),
                  'view_type': 'form',
                  'view_mode': 'form',
                  'view_id': res and res.id or False,
                  'res_model': 'purchase.shipment',
                  'type': 'ir.actions.act_window',
                  'target': 'current',
                  'res_id': self.id}

        return result

    @api.multi
    def action_edit_shipment_export(self):

        res = self.env.ref('lc_sales_product.view_shipment_export_form')

        result = {'name': _('Shipment'),
                  'view_type': 'form',
                  'view_mode': 'form',
                  'view_id': res and res.id or False,
                  'res_model': 'purchase.shipment',
                  'type': 'ir.actions.act_window',
                  'target': 'current',
                  'res_id': self.id,
                  'flags': {'initial_mode': 'edit'}}

        return result

    #For done_wizard
    @api.multi
    def action_done_export(self):
        res = self.env.ref('com_shipment.done_wizard')
        result = {
            'name': _('Do you want to done this shipment?'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'done.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result
    # State Change Actions

#########################################################################################
    @api.multi
    def action_add_invoice_export(self):
        res = self.env.ref('lc_sales_product.invoice_export_wizard')
        result = {
            'name': _('Please Enter The Information'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'invoice.export.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    @api.multi
    def action_to_sales_export(self):
        res = self.env.ref('lc_sales_product.to_sales_export_wizard')
        result = {
            'name': _('Please Enter The Information'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'to.sales.export.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    @api.multi
    def action_to_buyer_export(self):
        res = self.env.ref('lc_sales_product.to_buyer_export_wizard')
        result = {
            'name': _('Please Enter The Information'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'to.buyer.export.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    @api.multi
    def action_to_seller_bank_export(self):
        res = self.env.ref('lc_sales_product.to_seller_bank_export_wizard')
        result = {
            'name': _('Please Enter The Information'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'to.seller.bank.export.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    @api.multi
    def action_to_buyer_bank_export(self):
        res = self.env.ref('lc_sales_product.to_buyer_bank_export_wizard')
        result = {
            'name': _('Please Enter The Information'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'to.buyer.bank.export.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    @api.multi
    def action_to_maturity_export(self):
        res = self.env.ref('lc_sales_product.to_maturity_export_wizard')
        result = {
            'name': _('Please Enter The Information'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'to.maturity.export.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result