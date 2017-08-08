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
#    GNU Affero General Public License for more summary.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.osv import osv, fields


import logging
_logger = logging.getLogger(__name__)


class ProductProduct(osv.osv_memory):
    _name='product.barcode'
    _columns = {
        'product_id': fields.many2one('product.product', 'Product Name',  required=True),
        'parent_id': fields.many2one('product.barcode.print', 'Products to print Labels'),
        'qty': fields.integer('Number of Labels', help='How many labels to print', required=True),

    }
    _defaults = {
        'qty': 1
    }

class product_barcode_print(osv.osv_memory):
    _name = 'product.barcode.print'
    _description = 'Product Barcode Print'

    _columns = {
        'product_barcode_ids': fields.one2many('product.barcode', 'parent_id', 'Products to print labels'),
    }

    def _load_products(self, cr, uid, *args):
        id = args[0].get('active_id')
        product_barcode_ids = []

        if id:
            variants = self.pool['product.product'].search(cr, uid, [('product_tmpl_id', '=', id)])
            for record in variants:
                product_barcode_ids.append({
                    'product_id': record,
                    'parent_id': id
            })
        return product_barcode_ids

    _defaults = {
        'product_barcode_ids': _load_products
    }


    def print_report(self, cr, uid, ids, context=None):
        """
         To get the parameters and print the report
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return : retrun report
        """
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', []),'form':[]}
        res = self.read(cr, uid, ids, ['qty', 'product_ids'], context=context)
        res_data = self.browse(cr, uid, ids, context=context)
        res = res and res[0] or {}

        data={}
        for result in res_data.product_barcode_ids:
            data[result.product_id.id] = result.qty


        datas['form'] ={
            'product_ids':data,
            'id': res['id']
        }

        if res.get('id',False):
            datas['ids']=[res['id']]
        _logger.warning(datas)

        return self.pool['report'].get_action(cr, uid, [], 'product_barcode_qweb.report_product_barcode', data=datas, context=context)

    def print_single_report(self, cr, uid, ids, context=None):
        """
         To get the parameters and print the report
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return : retrun report
        """
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', []),'form':[]}
        res = self.read(cr, uid, ids, ['qty', 'product_ids'], context=context)
        res_data = self.browse(cr, uid, ids, context=context)
        res = res and res[0] or {}

        data={}
        for result in res_data.product_barcode_ids:
            data[result.product_id.id] = result.qty


        datas['form'] ={
            'product_ids':data,
            'id': res['id']
        }

        if res.get('id',False):
            datas['ids']=[res['id']]
        _logger.warning(datas)
        print datas

        return self.pool['report'].get_action(cr, uid, [], 'product_barcode_qweb.report_product_single_barcode', data=datas, context=context)

