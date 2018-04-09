# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class Picking(models.Model):
    _inherit = "stock.picking"

    check_mrr_button = fields.Boolean(defaulte=False,string='MRR Button Check')
    check_approve_button = fields.Boolean(defaulte=False,string='Approve Button Check',compute='_compute_approve_button',store=True)
    check_ac_approve_button = fields.Boolean(defaulte=False,string='AC Button Check',compute='_compute_approve_button',store=True)
    mrr_no = fields.Char('MRR No')

    pack_operation_product_ids = fields.One2many(
        'stock.pack.operation', 'picking_id', 'Non pack',
        domain=[('product_id', '!=', False)],
        states={'cancel': [('readonly', True)]})

    @api.multi
    @api.depends('location_dest_id','check_mrr_button','state')
    def _compute_approve_button(self):
        for picking in self:
            if picking.state == 'done':
                if picking.location_dest_id.name == 'Stock':
                    origin_picking_objs = self.search([('name','=',self.origin)])
                    if origin_picking_objs:
                        if origin_picking_objs[0].receive_type:
                            picking.check_approve_button = True
                            picking.check_ac_approve_button = False
                    else:
                        picking.check_ac_approve_button = True
                        picking.check_approve_button = False

                    if picking.check_mrr_button == True:
                        picking.check_approve_button = False
                        picking.check_ac_approve_button = False

    @api.multi
    def button_ac_approve(self):
        for picking in self:
            picking.check_approve_button = True
            picking.check_ac_approve_button = False


    @api.multi
    def button_approve(self):
        for picking in self:
            picking.check_mrr_button = 'True'
            new_seq = self.env['ir.sequence'].next_by_code('material.requisition')
            if new_seq:
                picking.mrr_no = new_seq

    @api.multi
    def button_print_mrr(self):
        data = {}

        return self.env['report'].get_action(self, 'stock_picking_mrr.report_mrr_doc', data=data)

class PackOperation(models.Model):
    _inherit = "stock.pack.operation"

    mrr_quantity = fields.Float('MRR Quantity', related = 'qty_done', digits=dp.get_precision('Product Unit of Measure'))
    check_mrr_button = fields.Boolean(defaulte=False,related = 'picking_id.check_mrr_button', string='MRR Button Check')