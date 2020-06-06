# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api,_
from odoo.exceptions import UserError


class ProductGateIn(models.Model):
    _name = 'stock.gate.in'
    _order = 'date desc, name desc, id desc'

    name = fields.Char(string='Name', index=True, readonly=True)
    create_by = fields.Char('Created By', size=100, readonly=True, states={'draft': [('readonly', False)]}, required=True)
    received = fields.Char('To Whom Received', size=100, readonly=True, states={'draft': [('readonly', False)]}, required=True)
    challan_bill_no = fields.Char('Challan Bill No', size=100, readonly=True, states={'draft': [('readonly', False)]}, required=True)
    truck_no = fields.Char('Truck/Vehicle No', size=100, readonly=True, states={'draft': [('readonly', False)]}, required=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.user.company_id, required=True)
    partner_id = fields.Many2one('res.partner', string='Supplier')
    date = fields.Date(string="Date", readonly=True, states={'draft': [('readonly', False)]}, required=True)
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirm"),
    ], default='draft', track_visibility='onchange')

    # change state, update line data, update 'purchase.shipment' model state
    @api.multi
    def action_confirm(self):
        self.state = 'confirm'
        self.shipping_line_ids.write({'state': 'confirm'})

    @api.multi
    def action_get_stock_picking(self):
        action = self.env.ref('stock.action_picking_tree_all').read([])[0]
        return action

    @api.multi
    def action_draft(self):
        self.state = 'draft'
        self.shipping_line_ids.write({'state': 'draft'})

    @api.constrains('challan_bill_no')
    def _check_unique_constraint(self):
        if self.partner_id and self.challan_bill_no:
            filters = [['challan_bill_no', '=ilike', self.challan_bill_no],['partner_id', '=', self.partner_id.id]]
            bill_no = self.search(filters)
            if len(bill_no) > 1:
                raise UserError(_('[Unique Error] Challan Bill must be unique for %s !')% self.partner_id.name)

    @api.constrains('shipping_line_ids')
    def _check_shipping_line_ids(self):
        if not self.shipping_line_ids:
            raise UserError(_('You cannot save %s which has no line.' % (self.name)))

    ####################################################
    # Override methods
    ####################################################
    #For create secquence
    @api.model
    def create(self, vals):
        requested_date = datetime.today().date()
        new_seq = self.env['ir.sequence'].next_by_code_new('stock.gate.in', requested_date) or '/'
        vals['name'] = new_seq
        return super(ProductGateIn, self).create(vals)

    @api.multi
    def unlink(self):
        for m in self:
            if m.state != 'draft':
                raise UserError(_('You can not delete in this state.'))
        return super(ProductGateIn, self).unlink()
