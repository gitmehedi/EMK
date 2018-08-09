from odoo import api, fields, models, _


class Shipment(models.Model):

    _inherit = 'purchase.shipment'

    invoice_id = fields.Many2one("account.invoice", string='Invoice Number', ondelete='cascade',
                                 domain=[('sale_type_id.sale_order_type', '=','lc_sales'),
                                         ('state', '=', 'open')])

    to_sales_date = fields.Date('Dispatch to Sales', track_visibility='onchange')
    to_buyer_date = fields.Date('Dispatch to Party', track_visibility='onchange')
    to_seller_bank_date = fields.Date('Seller Bank Receive', track_visibility='onchange')
    to_buyer_bank_date = fields.Date('Buyer Bank Receive', track_visibility='onchange')
    to_maturity_date = fields.Date('Maturity Date', track_visibility='onchange')
    bill_id = fields.Char('Bill ID', track_visibility='onchange')

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
         ('to_sales',"To Sales"),
         ('to_buyer',"To Buyer"),
         ('to_seller_bank',"To Seller Bank"),
         ('to_buyer_bank',"To Buyer Bank"),
         ('to_maturity', "To Maturity"),
         ('done', "Done"),
         ('cancel', "Cancel")], default='draft', track_visibility='onchange')



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