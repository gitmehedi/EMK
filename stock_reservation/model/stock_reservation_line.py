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

from openerp import models, fields, api
from openerp.addons.helper import validator

class StockReservationLine(models.Model):
    _name = 'stock.reservation.line'
    _description = 'Stock Reservation Line'
    
    
    product_id = fields.Many2one('product.product', required=True, string="Product")
    quantity = fields.Float(digits=(20, 2), string='Quantity', required=True, default=0.0)
    uom = fields.Many2one('product.uom', string="UOM",related='product_id.uom_id', readonly=True, store=True)
    uom_category = fields.Integer(invisible=True)

    stock_reservation_id = fields.Many2one('stock.reservation',"Stock Reservation")
    analytic_account_id = fields.Many2one(string='Analytic Account', 
                                          related='stock_reservation_id.analytic_account_id')
    max_resv_qty = fields.Float(digits=(20, 2), string='Max Reserve Qty', default=0.0)
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id and self.stock_reservation_id.source_loc_id:
            self.analytic_account_id = self.stock_reservation_id.analytic_account_id
            
            sql = '''
                 SELECT COALESCE(sum(qty),0) AS qty from (
                            SELECT  COALESCE(sum(sq.qty),0) AS qty
                                FROM stock_quant sq
                            where sq.product_id = %s and sq.location_id = %s and
                            owner_id is Null and 
                            reservation_id is Null
                            Group by sq.location_id,sq.product_id
                            UNION
                            SELECT COALESCE(sum(rq.reserve_quantity*(-1)),0) AS qty from reservation_quant rq
                            where  rq.product_id = %s and rq.location = %s
                                Group by rq.location, rq.product_id
                            ) as res
                ''' %(self.product_id.id, self.stock_reservation_id.source_loc_id.id, self.product_id.id, self.stock_reservation_id.source_loc_id.id)
            self.env.cr.execute(sql)
            result = self.env.cr.dictfetchone()
            self.max_resv_qty = result['qty']
    
    
   
    @api.multi
    def _validate_data(self, value):
        msg , filterInt = {}, {}
        
        filterInt['Quantity'] = value.get('quantity', False)
       
        msg.update(validator._validate_number(filterInt))
        validator.validation_msg(msg)
        
        return True
            

        
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        self._validate_data(vals)
        return super(StockReservationLine, self).create(vals)
   
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        return super(StockReservationLine, self).write(vals)
