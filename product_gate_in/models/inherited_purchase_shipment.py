from odoo import api, fields, models, _


class GateInShipmentProduct(models.Model):
    _inherit = 'purchase.shipment'

    gate_in_ids = fields.One2many('product.gate.in', 'ship_id', string='Gate Ins')
