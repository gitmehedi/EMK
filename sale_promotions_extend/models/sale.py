# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp

class SaleOrder(osv.osv):
    '''
    Sale Order
    '''
    _inherit = 'sale.order'
    
    def create(self, cr, uid, vals, context=None):
        #print "------32---------SaleOrder----create---------------------"
        res = super(SaleOrder, self).create(cr, uid, vals, context=context)
        
        if res:
            promotions_obj = self.pool.get('promos.rules')
            action_obj = self.pool.get('promos.rules.actions')
            
            order = self.browse(cr, uid, res, context)
            action_obj.clear_existing_promotion_lines(cr, uid, order, context)
            promotions_obj.apply_promotions(cr, uid, 
                                            res, context=None)
            
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        #print "-----45----------SaleOrder----write---------------------"
        res = super(SaleOrder, self).write(cr, uid, ids, vals, context)
        promotions_obj = self.pool.get('promos.rules')
        action_obj = self.pool.get('promos.rules.actions')
        for order in self.browse(cr, uid, ids, context):
            action_obj.clear_existing_promotion_lines(cr, uid, order, context)
            promotions_obj.apply_promotions(cr, uid, 
                                                     order.id, context=None)
        return res
    
    def apply_promotions(self, cursor, user, ids, context=None):
        """
        Applies the promotions to the given records
        @param cursor: Database Cursor
        @param user: ID of User
        @param ids: ID of current record.
        @param context: Context(no direct use).
        """
        #print "------65---------SaleOrder----apply_promotions---------------------"        
        promotions_obj = self.pool.get('promos.rules')
        action_obj = self.pool.get('promos.rules.actions')
        for order in self.browse(cursor, user, ids, context):
            action_obj.clear_existing_promotion_lines(cursor, user, order, context)
            promotions_obj.apply_promotions(cursor, user, 
                                            order.id, context=None)
            
        return True
            
SaleOrder()

class SaleOrderLine(osv.osv):
    '''
    Sale Order Line
    '''
    _inherit = "sale.order.line"
    
    def _get_discounted_unit_price(self, cr, uid, ids, 
                          name, arg, context=None):
        '''
        This function return the discounted unit price of the product.
        @param cr: Database Cursor
        @param uid: ID of User
        @param ids: ID of Current record.
        @param name: Name of the field which calls this function.
        @param arg: Any argument(here None).
        @param context: Context(no direct use).
        @return: Float
        '''
        res = {}

        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = (line.price_unit - (line.price_unit*line.discount/100)) or 0.0
            
        return res
    
    _columns = {
        'actual_unit_price': fields.float('Unit Price', digits_compute= dp.get_precision('Product Price'), readonly=True,),
        'discount_price': fields.function(
                    _get_discounted_unit_price, 
                    store=False, 
                    type='float',
                    string='Unit Price',
                    readonly = True,
                    help='Discounted Unit Price.'),
                }
    
    def _get_discount_price(self, cr, uid, unit_price, result):
        for val in result:
            #print val
            if val.find('F') > 0:
                val = val.replace('F','')
                
                try:
                    val = float(val)
                except:
                    val = 0.0
                unit_price = unit_price - val
            else:
                try:
                    val = float(val)
                except:
                    val = 0.0
                unit_price = unit_price - (unit_price * val / 100.0)
            #print unit_price
        return unit_price
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        #print "------127--------SaleOrderLine--------------product_id_change--------------------------------"
        #print product
        #Call Super Function
        res = super(SaleOrderLine, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
        #print res
        if product and res:

            #Set Product Actual Unit Price
            product = self.pool.get('product.product').browse(cr, uid, product, context)
            #print "---------------------------------------------------------------"
            #print res
            unit_price = product.list_price
            res['value'].update({'actual_unit_price': unit_price})
            #print res
            promotions_obj = self.pool.get('promos.rules')
            result = promotions_obj.apply_promotions_line(cr, uid, partner_id, date_order, product, context=context)
            
            #Set discounted unit price
            if result:
                unit_price = self._get_discount_price(cr, uid, unit_price, result)
                res['value'].update({'price_unit': unit_price})
            
        return res
    
SaleOrderLine()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: