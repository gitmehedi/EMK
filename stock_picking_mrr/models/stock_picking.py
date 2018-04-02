# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class Picking(models.Model):
    _inherit = "stock.picking"

    check_mrr_button = fields.Boolean('Button Check')
    mrr_no = fields.Char('MRR No')

    pack_operation_product_ids = fields.One2many(
        'stock.pack.operation', 'picking_id', 'Non pack',
        domain=[('product_id', '!=', False)],
        states={'cancel': [('readonly', True)]})

    @api.multi
    def button_approve(self):
        for picking in self:
            picking.check_mrr_button = 'True'
            new_seq = self.env['ir.sequence'].next_by_code('material.requisition')
            if new_seq:
                picking.mrr_no = new_seq

    @api.multi
    def process_report(self):
        data = {}

        return self.env['report'].get_action(self, 'stock_picking_mrr.report_mrr_doc', data=data)

class PackOperation(models.Model):
    _inherit = "stock.pack.operation"

    mrr_quantity = fields.Float('MRR Quantity', related = 'qty_done', digits=dp.get_precision('Product Unit of Measure'))