# -*- coding: utf-8 -*-
import time

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class Picking(models.Model):
    _inherit = "stock.picking"

    receive_type = fields.Selection([
        ('lc', 'LC'),
        ('loan', 'Loan'),
        ('credit', 'Credit'),
        ('tt', 'TT'),
        ('other', 'Other')],
        readonly=True, states={'draft': [('readonly', False)]})

    shipment_id = fields.Many2one(
        'purchase.shipment',
        string='Shipment Number',
        readonly=True,states={'draft': [('readonly', False)]},
        domain = "[('state','in',('cnf_clear', 'gate_in', 'done'))]")

    @api.onchange('receive_type')
    def onchange_receive_type(self):
        if self.receive_type:
            self.shipment_id = False
            self.challan_bill_no = False
            self.partner_id = False
            self.move_lines = []

    @api.onchange('shipment_id')
    def _onchange_shipment_id(self):
        if not self.shipment_id:
            return

        date_planned = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        if self.shipment_id.gate_in_ids:
            self.challan_bill_no = self.shipment_id.gate_in_ids[0].challan_bill_no or False
            self.partner_id = self.shipment_id.gate_in_ids[0].partner_id.id or False

        product_lines = []
        for ship_pro_line in self.shipment_id.shipment_product_lines:

            product_lines.append((0, 0,{
                'name': self.name,
                'origin': self.name,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'picking_type_id': self.picking_type_id.id,
                'date': date_planned,
                'date_expected': date_planned,
                'product_id': ship_pro_line.product_id.id,
                'product_uom': ship_pro_line.product_uom.id,
                'product_uom_qty': ship_pro_line.product_qty,
                'price_unit':ship_pro_line.price_unit,
                'state' : self.state,
            }))

        self.move_lines = product_lines

