from odoo import api, fields, models,_


class GateInShipmentProduct(models.Model):
    _inherit = 'purchase.shipment'

    gate_in_ids = fields.One2many('product.gate.in', 'ship_id', string='Gate Ins')

    #pull product_gate_in_form_view and add default add lc_id and ship_id in product_gate_in model
    @api.multi
    def action_create_gate_in_button(self):
        view = self.env.ref('product_gate_in.product_gate_in_form_view')

        return {
            'name': ('Gate'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.gate.in',
            'view_id': [view.id],
            'type': 'ir.actions.act_window',
            'context': {'default_lc_id': self.lc_id.id,'default_ship_id': self.id}

        }