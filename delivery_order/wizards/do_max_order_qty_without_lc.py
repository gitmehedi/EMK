from odoo import models, fields, api


class DOMaxOrderQtyWithoutLc(models.TransientModel):
    _name = 'max.delivery.without.lc.wizard'

    info_text = fields.Char(string='Info Text', default=lambda self: self.env.context.get('product_name'),
                            readonly=True)

    @api.one
    def update_state(self, context=None):
        if context['delivery_authorization_id']:
            delivery_authorization = self.env['delivery.authorization'].browse(context.get('delivery_authorization_id'))
            delivery_authorization.write({'state': 'validate'})
            ordered_qty = self.env['ordered.qty'].browse(context.get('ordered_qty_id'))
            if ordered_qty.available_qty > 0:
                ordered_qty.write({'available_qty': 0})
