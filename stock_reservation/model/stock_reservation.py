# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, exceptions, fields, models
from openerp.exceptions import except_orm
from openerp.tools.translate import _
from openerp import _
from openerp.exceptions import Warning

class StockReservation(models.Model):

    _name = 'stock.reservation'
    _description = 'Stock Reservation'
    
    date = fields.Date('Date', default=fields.Date.today, required=True, readonly=True, states={'draft':[('readonly', False)]})
    name = fields.Char("Reservation")
    warehouse_id = fields.Many2one('stock.warehouse', "Warehouse", required=True, readonly=True, states={'draft':[('readonly', False)]})
    state = fields.Selection([('draft', "Draft"), ('generate', "Generate"), ('confirmed', "Confirmed"), ('reserve', "Reserve"), ('release', "Release"), ('done', "Done"), ('cancel', "Cancel")],
                            default="draft", readonly=True, states={'draft':[('readonly', False)]})
    stock_reservation_line_ids = fields.One2many('stock.reservation.line', 'stock_reservation_id', string="Stock Reservation", readonly=True, states={'draft':[('readonly', False)]}, copy=True)
    
    source_loc_id = fields.Many2one('stock.location', 'Stock Location', required=True, readonly=True, states={'draft':[('readonly', False)]})
    
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', required=True, readonly=True, states={'draft':[('readonly', False)]})
    remarks = fields.Text(string="Remarks", size=300,
                          readonly=True, states={'draft':[('readonly', False)]})
    allocate_flag = fields.Integer(default=1)
    _rec_name = 'id'
    
    @api.multi
    @api.onchange('warehouse_id')
    def onchange_warehouse(self):
        if self.warehouse_id and self.allocate_flag == 1:
            self.source_loc_id = self.warehouse_id.lot_stock_id
    
    @api.multi
    def action_confirmed(self,vals):
        obj_stock_quant = self.env["stock.quant"]
        res_line = vals.get('stock_reservation_line_ids', False)
        loc_id = self.source_loc_id
        if self.stock_reservation_line_ids:
            for val in self.stock_reservation_line_ids:
                for line in val:
                    sql = '''
                         SELECT COALESCE(sum(qty),0) AS qty from (
                            SELECT  COALESCE(sum(sq.qty),0) AS qty
                                FROM stock_quant sq
                            where sq.product_id = %s and sq.location_id = %s
                            Group by sq.location_id,sq.product_id
                            UNION
                            SELECT COALESCE(sum(rq.reserve_quantity*(-1)),0) AS qty from reservation_quant rq
                            where  rq.product_id = %s and rq.location = %s
                                Group by rq.location, rq.product_id
                            ) as res
                    ''' %(line.product_id.id,loc_id.id,line.product_id.id,loc_id.id)
                    self.env.cr.execute(sql)
                    result = self.env.cr.dictfetchone()
                    if line.quantity > result['qty']:
                        raise Warning(_('Reserve Quantity can not be greater than stock quantity.'))
            
            self.state = "confirmed"
    
    @api.multi
    def action_cancel(self):
        self.state = "cancel"
     
    @api.multi
    def action_reserve(self):
        self.state = "reserve"
    '''     
    @api.multi
    def action_reserve(self):
        
        obj_stock_picking = self.env['stock.picking']
        pick_vals = {
                'picking_type_id': self.env['stock.picking.type'].search([('name', '=', 'Stock Reservation')], limit=1).id,
                'state':'assigned',
                'date':fields.Datetime.now(),
                'stock_reservation_id':self.id
                }
        picking_id = obj_stock_picking.create(pick_vals)
        self.state = 'reserve'
        if picking_id and self.stock_reservation_line_ids:
            for res in self:
                for line in res.stock_reservation_line_ids:
                        
                    obj_stock_move = self.env['stock.move']
                    move_vals = {
                        'name': line.product_id.name,
                        'date':fields.Datetime.now(),
                        'date_expected': fields.Datetime.now(),
                        'picking_id': picking_id.id,
                        'picking_type_id': self.env['stock.picking.type'].search([('name', '=', 'Stock Reservation')], limit=1).id,
                        'product_id': line.product_id.id,
                        'product_uom':line.uom.id,
                        'price_unit':line.product_id.standard_price or 0.0,
                        'product_uom_qty': line.quantity,
                        'location_id': self.source_loc_id.id,
                        'location_dest_id': self.analytic_resv_loc_id.id,
                        'state':'assigned',
                        
                    }
                    
                    move_id = obj_stock_move.create(move_vals)
    '''              
    @api.multi
    def write(self, vals):
        print "+++++++++++>>>>>>>>>>>>>>", vals
        print "+++++++++++>>>>>>>>>>>>>>self:", self.source_loc_id.id
#         obj_reservation_quant = self.env['reservation.quant']

        if('state' in vals):
            if(vals['state'] == 'reserve' or vals['state'] == 'release'):
                for res in self:
                    for line in res.stock_reservation_line_ids:
                        if (vals['state'] == 'reserve') or (vals['state'] == 'release' and self.allocate_flag == 3):
                            reservation_quant_obj = self.env['reservation.quant'].search([['product_id', '=', line.product_id.id], ['location', '=', self.source_loc_id.id], ['analytic_account_id', '=', line.analytic_account_id.id]])
                            print "reservation_quant_obj11", reservation_quant_obj
                        if vals['state'] == 'release' and self.allocate_flag == 2:
                            reservation_quant_obj = self.env['reservation.quant'].search([['product_id', '=', line.product_id.id], ['location', '=', self.source_loc_id.id], ['analytic_account_id', '=', line.analytic_account_id.id]])
                            print "reservation_quant_obj", reservation_quant_obj
                        
                        if not reservation_quant_obj:
                            move_vals = {
                                'product_id': line.product_id.id,
                                'reserve_quantity': line.quantity,
                                'uom':line.uom.id,
                                'location': self.source_loc_id.id,
                                'analytic_account_id':line.analytic_account_id.id
                            }
                                
                            move_id = reservation_quant_obj.create(move_vals)
                        else:
                            reserve_qty = 0;
                            if(self.allocate_flag == 1 or self.allocate_flag == 3):
                                reserve_qty = reservation_quant_obj.reserve_quantity + line.quantity
                            if(self.allocate_flag == 2):
                                reserve_qty = reservation_quant_obj.reserve_quantity - line.quantity
                            move_vals = {
                            'reserve_quantity': reserve_qty
                        }
                            
                            move_id = reservation_quant_obj.write(move_vals)  
        return super(StockReservation, self).write(vals)
    '''
    
    @api.multi
    @api.onchange('analytic_account_id')
    def onchange_analytic(self):
        if self.analytic_account_id:
            for line in self:
                for res in line.stock_reservation_line_ids:
                    res.analytic_account_id = self.analytic_account_id
    '''
