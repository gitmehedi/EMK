# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TdsVendorChallan(models.Model):
    _name = 'tds.vendor.challan'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'supplier_id desc'
    _description = 'TDS Vendor Challan'

    supplier_id = fields.Many2one('res.partner', string="Supplier")
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Operating Unit')
    date_from = fields.Date(string='From Date', required=True)
    date_to = fields.Date(string='To Date', required=True)
    line_ids = fields.One2many('tds.vendor.challan.line','parent_id',string='Vendor Challan')

    state = fields.Selection([
        ('draft', "Draft"),
        ('deposited', "Deposited"),
        ('distributed', "Distributed"),
    ], default='draft', track_visibility='onchange')

    @api.model
    def action_confirm(self):
        print "-----"

class TdsVendorChallanLine(models.Model):
    _name = 'tds.vendor.challan.line'

    supplier_id = fields.Many2one('res.partner', string="Supplier")
    provider_id = fields.Many2one('res.partner', string="Provided By")
    total_bill = fields.Float(String='Total Bill')
    undistributed_bill = fields.Float(String='Undistributed Bill')
    parent_id = fields.Many2one('tds.vendor.challan')



