# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv
import time

class stock_move_claim(osv.osv_memory):
    _description = "Scrap Claim Products"
    _name = "stock.move.claim"
    
    _columns = {
        'location_id': fields.many2one('stock.location', 'Location', required=True),
        'claim_id': fields.many2one('sale.warranty.claim', 'Warranty Claim', required=True),
    }
    
    _defaults = {
        'location_id': lambda *x: False
    }
    
    def default_get(self, cr, uid, fields, context=None):
        """ Get default values
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for default value
        @param context: A standard dictionary
        @return: default values of fields
        """
        if context is None:
            context = {}
        res = {}
        claim_ids = context['active_ids']
        if 'claim_id' in fields:
            res.update({'claim_id': claim_ids[0]})

        return res
    
    def move_scrap(self, cr, uid, ids, context=None):
        """ To move scrapped products
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs if we want more than one
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        claim_pool = self.pool.get('sale.warranty.claim')
        customer_loc = self.pool.get('stock.location').search(cr, uid, [('name','=','Customers')], context=context)[0] or False
        for data in self.browse(cr, uid, ids):
            vals = {
                    'auto_validate':True,
                    'date':time.strftime('%Y-%m-%d'),
                    'date_expected':time.strftime('%Y-%m-%d'),
                    'location_dest_id':data.location_id.id,
                    'location_id':customer_loc,
                    'name':data.claim_id.name,
                    'product_id':data.claim_id.warranty_id.product_id.id,
                    'product_qty':1,
                    'product_uom':data.claim_id.warranty_id.product_tmp_id.uom_id.id,
                    'scrapped':True,
                    'type': 'in',
                    }
            
            move_id = move_obj.create(cr, uid, vals, context=context)
            move_obj.action_done(cr, uid, [move_id], context=context)
            claim_pool.receive(cr, uid, [data.claim_id.id], context=context)
            
        return {'type': 'ir.actions.act_window_close'}
    
stock_move_claim()