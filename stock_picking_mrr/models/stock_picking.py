# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class Picking(models.Model):
    _inherit = "stock.picking"

    check_mrr_button = fields.Boolean(default=False,string='MRR Button Check')
    check_approve_button = fields.Boolean(default=False,string='Approve Button Check',compute='_compute_approve_button',store=True)
    check_ac_approve_button = fields.Boolean(default=False,string='AC Button Check',compute='_compute_approve_button',store=True)
    mrr_no = fields.Char('MRR No')
    mrr_date = fields.Date('MRR date')

    pack_operation_product_ids = fields.One2many(
        'stock.pack.operation', 'picking_id', 'Non pack',
        domain=[('product_id', '!=', False)],
        states={'cancel': [('readonly', True)]})

    @api.multi
    @api.depends('receive_type','location_dest_id','check_mrr_button','state')
    def _compute_approve_button(self):
        for picking in self:
            if picking.transfer_type == 'receive' and picking.state == 'done' and picking.location_dest_id.name == 'Stock':
                # if picking.state == 'done':
                #     if picking.location_dest_id.name == 'Stock':
                origin_picking_objs = self.search([('name','=',picking.origin)])
                if origin_picking_objs:
                    if origin_picking_objs[0].receive_type in ['lc','loan']:
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
            requested_date = datetime.today().date()
            new_seq = self.env['ir.sequence'].next_by_code_new('material.requisition',requested_date)
            if new_seq:
                picking.mrr_no = new_seq
                picking.mrr_date = datetime.today().date()

    @api.multi
    def button_print_mrr(self):
        data = {}

        data['origin'] = self.origin
        data['mrr_no'] = self.mrr_no
        data['mrr_date'] = self.mrr_date

        return self.env['report'].get_action(self, 'stock_picking_mrr.report_mrr_doc', data=data)

class PackOperation(models.Model):
    _inherit = "stock.pack.operation"

    mrr_quantity = fields.Float('MRR Quantity', related = 'qty_done', digits=dp.get_precision('Product Unit of Measure'))
    check_mrr_button = fields.Boolean(defaulte=False,related = 'picking_id.check_mrr_button', string='MRR Button Check')