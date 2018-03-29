# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class Picking(models.Model):
    _inherit = "stock.picking"

    check_mrr_button = fields.Boolean('Button Check')

    pack_operation_product_ids = fields.One2many(
        'stock.pack.operation', 'picking_id', 'Non pack',
        domain=[('product_id', '!=', False)],
        states={'cancel': [('readonly', True)]})

    @api.multi
    def button_approve(self):
        for picking in self:
            picking.check_mrr_button = 'True'

class PackOperation(models.Model):
    _inherit = "stock.pack.operation"

    mrr_quantity = fields.Float('MRR Quantity', related = 'qty_done', digits=dp.get_precision('Product Unit of Measure'))

    # @api.onchange('mrr_quantity')
    # def _onchange_mrr_quantity(self):
    #     move_objs = self.env['stock.move'].search([('id', 'in', self.picking_id.move_lines.ids)])
    #     for move_obj in move_objs:
    #         print move_obj
         # if self.mrr_quantity:
        #     move_obj.write({'mrr_quantity': self.mrr_quantity})

#
# class StockMove(models.Model):
#     _inherit = "stock.move"
#
#     mrr_quantity = fields.Float('MRR Quantity',  digits=dp.get_precision('Product Unit of Measure'))
# related = 'picking_id.pack_operation_product_ids.mrr_quantity',
