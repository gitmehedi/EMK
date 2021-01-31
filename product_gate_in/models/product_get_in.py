# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api,_
from odoo.exceptions import UserError


class ProductGateIn(models.Model):
    _name = 'product.gate.in'
    _order = 'date desc, name desc, id desc'

    name = fields.Char(string='Name', index=True, readonly=True)
    create_by = fields.Char('Carried By',size=100, readonly=True, states={'draft': [('readonly', False)]},required=True)
    received = fields.Char('To Whom Received',size=100, readonly=True, states={'draft': [('readonly', False)]},required=True)

    challan_bill_no = fields.Char('Challan Bill No',size=100, readonly=True, states={'draft': [('readonly', False)]},required=True)
    truck_no = fields.Char('Truck/Vehicle No',size=100, readonly=True, states={'draft': [('readonly', False)]},required=True)

    shipping_line_ids = fields.One2many('product.gate.line','parent_id',required=True,readonly=True,states={'draft': [('readonly', False)]})
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id,
                                        readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string='Company', readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.user.company_id, required=True)
    ship_id = fields.Many2one('purchase.shipment', string='Shipment Number',
                              states={'confirm': [('readonly', True)]},
                              domain="['&','&','&',('operating_unit_id','=',operating_unit_id),('state','in',('cnf_clear', 'gate_in', 'done')),('lc_id.state','!=','done'),('lc_id.state','!=','cancel')]")
    partner_id = fields.Many2one('res.partner', string='Supplier')

    date = fields.Date(string="Date",readonly=True, states={'draft': [('readonly', False)]},required=True)
    receive_type = fields.Selection([('lc', "LC"), ('others', "Others")], readonly=True,
                                    required=True,states={'draft': [('readonly', False)]}, track_visibility='onchange')

    picking_id = fields.Many2one('stock.picking', 'Picking')

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirm"),
    ], default='draft',track_visibility='onchange')

    # NSF=Not Store Field
    lc_id = fields.Many2one('letter.credit', string='LC Number', store=False, search='_search_shipment_lc_id')

    @api.model
    def _search_shipment_lc_id(self, operator, value):
        res = []
        lc_ids = self.env['letter.credit'].search([('name', operator, value)])
        ship_ids = self.env['purchase.shipment'].search([('lc_id', 'in', lc_ids.ids)])
        gate_in_ids = self.env['product.gate.in'].search([('ship_id', 'in', ship_ids.ids)])
        res.append(('id', 'in', gate_in_ids.ids))

        return res

    # change state, update line data, update 'purchase.shipment' model state
    @api.multi
    def action_confirm(self):
        self.state = 'confirm'
        self.shipping_line_ids.write({'state': 'confirm'})
        self.ship_id.write({'state':'gate_in'})
        if self.receive_type == 'lc':
            if self.shipping_line_ids:
                picking_id = self._create_pickings_and_procurements()
                picking_objs = self.env['stock.picking'].search([('id','=',picking_id)])
                picking_objs.action_confirm()
                picking_objs.force_assign()
                self.write({'picking_id': picking_id})

    @api.model
    def _create_pickings_and_procurements(self):
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        location_obj = self.env['stock.location']
        picking_id = False
        for line in self.shipping_line_ids:
            date_planned = datetime.now()
            location_id = location_obj.search([('usage', '=', 'supplier')], limit=1)
            location_dest_id = location_obj.search(
                [('operating_unit_id', '=', self.operating_unit_id.id), ('name', '=', 'Input')], limit=1)
            if line.product_id:
                if not picking_id:
                    picking_type = self.env['stock.picking.type'].search(
                        [('code', '=', 'incoming'), ('warehouse_id.operating_unit_id', '=', self.operating_unit_id.id),
                         ('default_location_dest_id', '=', location_dest_id.id)], order='id ASC', limit=1)

                    # pick_name = self.env['ir.sequence'].next_by_code('stock.picking')
                    pick_name = self.env['stock.picking.type'].browse(picking_type.id).sequence_id.next_by_id()

                    res = {
                        'receive_type': self.receive_type,
                        'transfer_type': 'receive',
                        'shipment_id': self.ship_id.id,
                        'picking_type_id': picking_type.id,
                        'priority': '1',
                        'move_type': 'direct',
                        'company_id': self.company_id.id,
                        'operating_unit_id': self.operating_unit_id.id,
                        'state': 'draft',
                        # 'name': self.name,
                        # 'origin': self.name,
                        'name': pick_name,
                        'origin': self.ship_id.lc_id.name,
                        'date': date_planned,
                        'location_id': location_id.id,
                        'location_dest_id': location_dest_id.id,
                        'challan_bill_no': self.challan_bill_no,
                        'partner_id': self.partner_id.id,
                    }
                    if self.company_id:
                        vals = dict(res, company_id=self.company_id.id)

                    picking = picking_obj.create(res)
                    if picking:
                        picking_id = picking.id

                moves = {
                    # 'name': self.name,
                    # 'origin': self.name or self.picking_id.name,
                    'name': line.product_id.name,
                    'origin': self.ship_id.lc_id.name,
                    'location_id': location_id.id,
                    'location_dest_id': location_dest_id.id,
                    'picking_id': picking_id or False,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_qty,
                    'product_uom': line.product_uom.id,
                    'price_unit': line.price_unit,
                    'date': date_planned,
                    'date_expected': date_planned,
                    'picking_type_id': picking_type.id,
                    'warehouse_id': picking_type.warehouse_id.id,
                    'state': 'draft',

                }
                move_obj.create(moves)

        return picking_id

    @api.multi
    def action_get_stock_picking(self):
        action = self.env.ref('stock.action_picking_tree_all').read([])[0]
        action['domain'] = ['|', ('id', '=', self.picking_id.id), ('origin', '=', self.ship_id.lc_id.name)]
        return action

    @api.multi
    def action_draft(self):
        self.state = 'draft'
        self.shipping_line_ids.write({'state': 'draft'})

    @api.onchange('receive_type')
    def _onchange_receive_type(self):
        if self.receive_type != 'lc':
            self.ship_id = None

    @api.one
    @api.constrains('date')
    def _check_date(self):
        if self.date < self.ship_id.shipment_date:
            raise UserError('Gate In Date can not be less then Shipment date!!!')


    # change data and line data depands on ship_id
    @api.onchange('ship_id')
    def set_products_info_automatically(self):

        self.partner_id = False
        self.truck_no = False
        if self.ship_id:
            val = []
            sale_order_obj = self.env['purchase.shipment'].search([('id', '=', self.ship_id.id)])

            if sale_order_obj:
                self.lc_id = sale_order_obj.lc_id.id
                self.partner_id = sale_order_obj.lc_id.second_party_beneficiary
                self.truck_no = sale_order_obj.vehical_no

                for record in sale_order_obj.shipment_product_lines:
                    val.append((0, 0, {'product_id': record.product_id.id,
                                       'product_qty': record.product_qty,
                                       'product_uom': record.product_uom.id,
                                       'price_unit': record.price_unit,
                                       'name': record.name,
                                       'date_planned': record.date_planned,
                                       }))

            self.shipping_line_ids = val

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
    def create(self,vals):
        requested_date = datetime.today().date()
        new_seq = self.env['ir.sequence'].next_by_code_new('product.gate.in', requested_date) or '/'
        vals['name'] = new_seq
        return super(ProductGateIn, self).create(vals)

    @api.multi
    def unlink(self):
        for m in self:
            if m.state != 'draft':
                raise UserError(_('You can not delete in this state.'))
        return super(ProductGateIn, self).unlink()



class ShipmentProductLine(models.Model):
    _name = 'product.gate.line'
    _description = 'Product'
    _order = "date_planned desc"

    name = fields.Text(string='Description')
    product_id = fields.Many2one('product.product', string='Product',
                                change_default=True)
    date_planned = fields.Date(string='Scheduled Date', index=True)
    product_uom = fields.Many2one(related='product_id.uom_id',comodel='product.uom',string='UOM',store=True)
    price_unit = fields.Float(string='Unit Price')
    product_qty = fields.Float(string='Quantity')
    parent_id = fields.Many2one('product.gate.in',
                                string='Gate In')

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirm"),
    ], default='draft')

    ####################################################
    # Business methods
    ####################################################

    @api.one
    @api.constrains('product_qty')
    def _check_product_qty(self):
        if self.product_qty < 0:
            raise UserError('You can\'t give negative value!!!')
