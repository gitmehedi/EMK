from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ShipmentLocal(models.Model):

    _inherit = 'purchase.shipment'

    fob_value = fields.Float(string='FOB Value')
    feright_value = fields.Float(string='Feright Value', compute='_compute_feright_value', store=False)
    is_print_cfr = fields.Boolean(string='Is Print CFR')

    invoice_number_dummy = fields.Char(string='Invoice Number (Dummy)', track_visibility='onchange')
    truck_receipt_no = fields.Char(string='BL/Truck Receipt No.')
    bl_date = fields.Date(string='BL Date')
    cylinder_details = fields.Text(string='Cylinder Details')

    @api.one
    def _compute_feright_value(self):
        self.feright_value = None
        if self.fob_value > 0:
            self.feright_value = self.invoice_value - self.fob_value

    @api.onchange('fob_value')
    def _onchange_fob_value(self):
        self.feright_value = None
        if self.fob_value > 0:
            self.feright_value = self.invoice_value - self.fob_value

    @api.multi
    def action_doc_receive_export_foreign(self):
        res = self.env.ref('lc_sales_product_foreign.doc_receive_wizard_export_foreign')
        result = {
            'name': _('Please Enter Shipment Products'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'doc.receive.wizard.export.foreign',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    @api.multi
    def action_add_invoice_export_foreign(self):
        res = self.env.ref('lc_sales_product_foreign.invoice_export_wizard_foreign')
        result = {
            'name': _('Please Enter The Information'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'invoice.export.wizard.foreign',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    @api.multi
    def action_to_seller_bank_export_foreign(self):
        res = self.env.ref('lc_sales_product_foreign.to_seller_bank_export_foreign_wizard')
        result = {
            'name': _('Please Enter The Information'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'to.seller.bank.export.foreign.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    @api.multi
    def action_to_buyer_bank_export_foreign(self):
        res = self.env.ref('lc_sales_product_foreign.to_buyer_bank_export_foreign_wizard')
        result = {
            'name': _('Please Enter The Information'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'to.buyer.bank.export.foreign.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    @api.multi
    def action_to_maturity_export_foreign(self):
        res = self.env.ref('lc_sales_product_foreign.to_maturity_export_wizard_foreign')
        result = {
            'name': _('Please Enter The Information'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'to.maturity.export.wizard.foreign',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    # For done_wizard
    @api.multi
    def action_done_export_foreign(self):
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
    # ##########################################################################################



    @api.multi
    def action_view_shipment_export_foreign(self):

        res = self.env.ref('lc_sales_product_foreign.view_shipment_export_form')

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
    def action_edit_shipment_export_foreign(self):

        res = self.env.ref('lc_sales_product_foreign.view_shipment_export_form')

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



#########################################################################################


    # @api.multi
    # def action_to_sales_export_foreign(self):
    #     res = self.env.ref('lc_sales_product_foreign.to_sales_export_wizard')
    #     result = {
    #         'name': _('Please Enter The Information'),
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'view_id': res and res.id or False,
    #         'res_model': 'to.sales.export.wizard',
    #         'type': 'ir.actions.act_window',
    #         'nodestroy': True,
    #         'target': 'new',
    #     }
    #     return result
    #
    # @api.multi
    # def action_to_buyer_export_foreign(self):
    #     res = self.env.ref('lc_sales_product_foreign.to_buyer_export_wizard')
    #     result = {
    #         'name': _('Please Enter The Information'),
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'view_id': res and res.id or False,
    #         'res_model': 'to.buyer.export.wizard',
    #         'type': 'ir.actions.act_window',
    #         'nodestroy': True,
    #         'target': 'new',
    #     }
    #     return result
    #
    #
    #
