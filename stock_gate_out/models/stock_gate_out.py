# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api,_
from odoo.exceptions import UserError


class StockGateOut(models.Model):
    _name = 'stock.gate.out'
    _inherit = ['mail.thread']
    _order = 'date desc, name desc, id desc'

    name = fields.Char(string='Name', index=True, readonly=True)
    create_by = fields.Char('Delivered By', size=100, readonly=True, states={'draft': [('readonly', False)]}, required=True, track_visibility='onchange')
    received = fields.Char('To Whom Received', size=100, readonly=True, states={'draft': [('readonly', False)]}, required=True, track_visibility='onchange')
    challan_bill_no = fields.Char('Challan Bill No', size=100, readonly=True, states={'draft': [('readonly', False)]}, required=True, track_visibility='onchange')
    truck_no = fields.Char('Truck/Vehicle No', size=100, readonly=True, states={'draft': [('readonly', False)]}, required=True, track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.user.company_id, required=True)
    partner_id = fields.Many2one('res.partner', string='Supplier', readonly=True, states={'draft': [('readonly', False)]})
    date = fields.Date(string="Date", readonly=True, states={'draft': [('readonly', False)]}, required=True, track_visibility='onchange')
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirm"),
    ], default='draft', track_visibility='onchange')

    @api.model
    def create(self, vals):
        requested_date = datetime.today().date()
        new_seq = self.env['ir.sequence'].next_by_code_new('stock.gate.out', requested_date) or '/'
        vals['name'] = new_seq
        return super(StockGateOut, self).create(vals)

    @api.constrains('challan_bill_no')
    def _check_unique_constraint(self):
        if self.partner_id and self.challan_bill_no:
            filters = [['challan_bill_no', '=ilike', self.challan_bill_no],['partner_id', '=', self.partner_id.id]]
            bill_no = self.search(filters)
            if len(bill_no) > 1:
                raise UserError(_('[Unique Error] Challan Bill must be unique for %s !')% self.partner_id.name)

    @api.multi
    def action_confirm(self):
        self.state = 'confirm'

    @api.multi
    def action_get_stock_picking(self):
        action = self.env.ref('stock.action_picking_tree_all').read([])[0]
        return action

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def unlink(self):
        for m in self:
            if m.state != 'draft':
                raise UserError(_('You can not delete in this state.'))
        return super(StockGateOut, self).unlink()
