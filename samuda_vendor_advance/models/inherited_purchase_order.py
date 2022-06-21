from odoo import models, fields, api, _


class InheritedPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    vendor_advance_line = fields.One2many('vendor.advance', 'purchase_order_id', string='Vendor Advances', readonly=True)

    def button_advance_payment(self):
        result = {
            'name': _('Vendor Advance'),
            'view_type': 'form',

            'view_mode': 'form',
            'view_id': self.env.ref("samuda_vendor_advance.view_vendor_advance_form").id,
            'res_model': 'vendor.advance',
            'type': 'ir.actions.act_window',
            'context': {'default_purchase_order_id': self.id, 'default_partner_id': self.partner_id.id,
                        'default_operating_unit_id': self.operating_unit_id.id},
        }
        return result
