# -*- coding: utf-8 -*-
import time
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class StockPickingLoan(models.Model):
    _inherit = "stock.picking"

    loan_id = fields.Many2one(
        'item.borrowing',
        string='Loan Number',
        readonly=True, states={'draft': [('readonly', False)]})

    @api.onchange('receive_type')
    def onchange_receive_type(self):
        if self.receive_type:
            self.loan_id = False
            self.challan_bill_no = False
            self.move_lines = []

    @api.onchange('loan_id')
    def _onchange_loan_id(self):
        if not self.loan_id:
            return

        date_planned = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        self.partner_id = self.loan_id.partner_id.id or False

        product_lines = []
        for loan_pro_line in self.loan_id.item_lines:
            product_lines.append((0, 0, {
                'name': self.name,
                'origin': self.name,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'picking_type_id': self.picking_type_id.id,
                'date': date_planned,
                'date_expected': date_planned,
                'product_id': loan_pro_line.product_id.id,
                'product_uom': loan_pro_line.product_uom.id,
                'product_uom_qty': loan_pro_line.product_uom_qty,
                'price_unit': loan_pro_line.price_unit,
                'state': self.state,
            }))

        self.move_lines = product_lines