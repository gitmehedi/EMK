from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ShipmentLocal(models.Model):

    _inherit = 'purchase.shipment'

    feright_value = fields.Float(string='Freight Value')
    fob_value= fields.Float(string='FOB Value', compute='_compute_fob_value', store=False)
    is_print_cfr = fields.Boolean(string='Is Print CFR')
    invoice_number_dummy = fields.Char(string='Invoice Number (Dummy)', track_visibility='onchange')
    invoice_date_dummy = fields.Date(string='Invoice Date (Dummy)', track_visibility='onchange')
    truck_receipt_no = fields.Char(string='BL/Truck Receipt No.')
    bl_date = fields.Date(string='BL Date')
    cylinder_details = fields.Text(string='Cylinder Details')
    container_no = fields.Char(string='Container No.')
    mother_vessel = fields.Char(string='Mother Vessel')
    landing_port_country_id = fields.Many2one('res.country', 'Landing',related='lc_id.landing_port_country_id')
    discharge_port_country_id = fields.Many2one('res.country', 'Discharge', related='lc_id.discharge_port_country_id')
    transshipment_country_id = fields.Many2one('res.country', 'Transshipment Country', related='lc_id.transshipment_country_id')
    shipment_country_id = fields.Many2one('res.country', 'Transshipment Country', related='lc_id.transshipment_country_id')
    trans_shipment = fields.Boolean(string='Allow Trans. Shipment', related='lc_id.trans_shipment')
    eta_trans_shipment_date = fields.Date(string='ETA(Trans Shipment)')
    etd_trans_shipment_date = fields.Date(string='ETD(Trans Shipment)')

    @api.one
    def _compute_fob_value(self):
        self.fob_value = None
        if self.feright_value > 0:
            self.fob_value = self.invoice_value - self.feright_value

    @api.onchange('feright_value')
    def _onchange_feright_value(self):
        self.fob_value = None
        if self.feright_value > 0:
            self.fob_value = self.invoice_value - self.feright_value

    # @api.one
    # def _compute_feright_value(self):
    #     self.feright_value = None
    #     if self.fob_value > 0:
    #         self.feright_value = self.invoice_value - self.fob_value

    # @api.onchange('fob_value')
    # def _onchange_fob_value(self):
    #     self.feright_value = None
    #     if self.fob_value > 0:
    #         self.feright_value = self.invoice_value - self.fob_value

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
