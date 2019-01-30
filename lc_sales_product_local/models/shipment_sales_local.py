from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ShipmentLocal(models.Model):

    _inherit = 'purchase.shipment'

    @api.multi
    def action_doc_receive_export(self):
        res = self.env.ref('lc_sales_product_local.doc_receive_wizard_export')
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

        res = self.env.ref('lc_sales_product_local.view_shipment_export_form')

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

        res = self.env.ref('lc_sales_product_local.view_shipment_export_form')

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
        res = self.env.ref('lc_sales_product_local.invoice_export_wizard')
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
        res = self.env.ref('lc_sales_product_local.to_sales_export_wizard')
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
        res = self.env.ref('lc_sales_product_local.to_buyer_export_wizard')
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
        res = self.env.ref('lc_sales_product_local.to_seller_bank_export_wizard')
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
        res = self.env.ref('lc_sales_product_local.to_buyer_bank_export_wizard')
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
        res = self.env.ref('lc_sales_product_local.to_maturity_export_wizard')
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