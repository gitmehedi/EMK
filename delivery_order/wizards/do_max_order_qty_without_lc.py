from odoo import models, fields, api


class DOMaxOrderQtyWithoutLc(models.Model):
    _name = 'max.delivery.without.lc.wizard'

    info_text = fields.Char(string='Info Text', default=lambda self: self.env.context.get('product_name'),
                            readonly=True)

    @api.one
    def update_state(self, context=None):
        if context['delivery_order_id']:
            delivery_order_pool = self.env['delivery.order'].search([('id', '=', context['delivery_order_id'])])
            delivery_order_pool.write({'state': 'approve'})  # second approval
