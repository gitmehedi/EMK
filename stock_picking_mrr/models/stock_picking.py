# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class Picking(models.Model):
    _inherit = "stock.picking"

    check_mrr_button = fields.Boolean(default=False,string='MRR Button Check')
    check_approve_button = fields.Boolean(default=False,string='Approve Button Check',compute='_compute_approve_button',store=True)
    check_ac_approve_button = fields.Boolean(default=False,string='AC Button Check',compute='_compute_approve_button',store=True)
    mrr_no = fields.Char('MRR No',track_visibility="onchange")
    mrr_date = fields.Date('MRR date',track_visibility="onchange")
    approval_comment = fields.Char('Status', track_visibility='onchange')

    @api.multi
    @api.depends('receive_type','location_dest_id','check_mrr_button','state')
    def _compute_approve_button(self):
        for picking in self:
            if picking.state == 'done' and picking.location_dest_id.name == 'Stock':
                # Search from anticipatory stock
                if picking.check_mrr_button:
                    picking.check_ac_approve_button = False
                    picking.check_approve_button = False
                else:
                    # Search from anticipatory stock
                    origin_picking_objs = self.search(['|', ('name', '=', picking.origin), ('origin', '=', picking.origin)],
                                                      order='id ASC', limit=1)
                    # if anticipatory then conditionally search that its type
                    if origin_picking_objs:
                        if origin_picking_objs.receive_type == 'loan':
                            picking.check_ac_approve_button = False
                            picking.check_approve_button = False
                        else:
                            picking.check_ac_approve_button = True
                            picking.check_approve_button = False
                    else:
                        picking.check_ac_approve_button = True
                        picking.check_approve_button = False

    @api.multi
    def button_ac_approve(self):
        for picking in self:
            picking.approval_comment = 'Accounts Validate'
            picking.check_approve_button = True
            picking.check_ac_approve_button = False

    @api.multi
    def button_approve(self):
        for picking in self:
            picking.approval_comment = 'Final Approval'
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
        data['self_picking_id'] = self.id
        data['mrr_no'] = self.mrr_no
        data['mrr_date'] = self.mrr_date

        return self.env['report'].get_action(self, 'stock_picking_mrr.report_mrr_doc', data=data)

class PackOperation(models.Model):
    _inherit = "stock.pack.operation"

    mrr_quantity = fields.Float('MRR Quantity', related = 'qty_done', digits=dp.get_precision('Product Unit of Measure'))
    check_mrr_button = fields.Boolean(defaulte=False,related = 'picking_id.check_mrr_button', string='MRR Button Check')