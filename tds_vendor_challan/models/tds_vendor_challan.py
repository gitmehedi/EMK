from odoo import models, fields, api


class TdsVendorChallan(models.Model):
    _name = 'tds.vendor.challan'
    _inherit = ['mail.thread']
    _order = 'supplier_id desc'
    _rec_name = 'supplier_id'
    _description = 'TDS Vendor Challan'

    supplier_id = fields.Many2one('res.partner', string="Supplier", track_visibility='onchange')
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Operating Unit', track_visibility='onchange')
    date_from = fields.Date(string='From Date', required=True, track_visibility='onchange')
    date_to = fields.Date(string='To Date', required=True, track_visibility='onchange')
    line_ids = fields.One2many('tds.vendor.challan.line','parent_id',string='Vendor Challan', select=True, track_visibility='onchange')

    state = fields.Selection([
        ('draft', "Draft"),
        ('deposited', "Deposited"),
        ('distributed', "Distributed"),
    ], default='draft', track_visibility='onchange')

    @api.one
    def action_deposited(self):
        self.state = 'deposited'
        self.line_ids.write({'state':'deposited'})

    @api.one
    def action_distributed(self):
        self.state = 'distributed'
        self.line_ids.write({'state':'distributed'})


class TdsVendorChallanLine(models.Model):
    _name = 'tds.vendor.challan.line'

    supplier_id = fields.Many2one('res.partner', string="Supplier")
    provider_id = fields.Many2one('res.partner', string="Provided By")
    total_bill = fields.Float(String='Total Bill')
    undistributed_bill = fields.Float(String='Undistributed Bill')
    parent_id = fields.Many2one('tds.vendor.challan')

    state = fields.Selection([
        ('draft', "Draft"),
        ('deposited', "Deposited"),
        ('distributed', "Distributed"),
    ], default='draft', track_visibility='onchange')



