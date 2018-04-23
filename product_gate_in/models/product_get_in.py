# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api,_

class productGateIn(models.Model):
    _name = 'product.gate.in'


    name = fields.Char(string='Name', index=True, readonly=True)
    create_by = fields.Char('Carried By', readonly=True, states={'draft': [('readonly', False)]})
    received = fields.Char('To Whom Received', readonly=True, states={'draft': [('readonly', False)]})

    challan_bill_no = fields.Char('Challan Bill No', readonly=True, states={'draft': [('readonly', False)]})
    truck_no = fields.Char('Track/Vehical No', readonly=True, states={'draft': [('readonly', False)]})

    shipping_line_ids = fields.One2many('product.gate.line','parent_id')
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id,
                                        readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string='Company', readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.user.company_id, required=True)
    ship_id = fields.Many2one('purchase.shipment', string='Shipment Number',
                            states={'confirm': [('readonly', True)]},
                            domain="['&','&','&',('operating_unit_id','=',operating_unit_id),('state','in',('cnf_clear', 'gate_in', 'done')),('lc_id.state','!=','done'),('lc_id.state','!=','cancel')]")


    date = fields.Date(string="Date")
    receive_type = fields.Selection([
        ('lc', "LC"),
        ('loan', "Loan"),
        ('others', "Others"),

    ])

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirm"),
    ], default='draft')

    #change state, update line data, update 'purchase.shipment' model state
    @api.multi
    def action_confirm(self):
        self.state = 'confirm'
        self.shipping_line_ids.write({'state': 'confirm'})
        self.ship_id.write({'state':'gate_in'})

    @api.multi
    def action_draft(self):
        self.state = 'draft'
        self.shipping_line_ids.write({'state': 'draft'})

    #For create secquence
    @api.model
    def create(self,vals):
        requested_date = datetime.strptime(datetime.today(), "%Y-%m-%d %H:%M:%S").date()
        new_seq = self.env['ir.sequence'].next_by_code_new('item.borrowing', requested_date)
        seq = self.env['ir.sequence'].next_by_code('product.gate.in') or '/'
        vals['name'] = seq
        return super(productGateIn, self).create(vals)


    # change data and line data depands on ship_id
    @api.onchange('ship_id')
    def set_products_info_automatically(self):
        if self.ship_id:
            val = []
            sale_order_obj = self.env['purchase.shipment'].search([('id', '=', self.ship_id.id)])

            if sale_order_obj:
                self.lc_id = sale_order_obj.lc_id.id

                for record in sale_order_obj.shipment_product_lines:
                    val.append((0, 0, {'product_id': record.product_id.id,
                                       'product_qty': record.product_qty,
                                       'product_uom': record.product_uom.id,
                                       'name': record.name,
                                       'date_planned': record.date_planned,
                                       }))

            self.shipping_line_ids = val


class ShipmentProductLine(models.Model):
    _name = 'product.gate.line'
    _description = 'Product'
    _order = "date_planned desc"

    name = fields.Text(string='Description')
    product_id = fields.Many2one('product.product', string='Product',
                                change_default=True)
    date_planned = fields.Date(string='Scheduled Date', index=True)
    product_uom = fields.Many2one('product.uom',
                                  string='UOM')
    product_qty = fields.Float(string='Quantity',states={'confirm': [('readonly', True)]})
    parent_id = fields.Many2one('product.gate.in',
                                string='Purchase Shipment')

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirm"),
    ], default='draft')
