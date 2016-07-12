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
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval
import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round
from openerp import tools
# from openerp.exceptions import UserError
import time

class stock_inventory_wizard(osv.osv_memory):

    _name = 'stock.inventory.wizard'
    _columns = {
        'date_from': fields.date("Date from", required=True),
        'date_to': fields.date("Date to", required=True),
        'location_id': fields.many2one('stock.location', 'Location', required=True),
    }
    
    _defaults = {
               'date_from': lambda *a: time.strftime('%Y-%m-%d'),
               'date_to': lambda *a: time.strftime('%Y-%m-%d'),
               }
    

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}

        res = self.browse(cr, uid, ids, context=context)
        res = res and res[0] or {}
        
#         ctx = context.copy()
#         ctx['date_from'] = res['date_from']
#         ctx['date_to'] = res['date_to']
#         ctx['location_id'] = res['location_id']
        
        tools.drop_view_if_exists(cr, 'stock_inventory_report')
        date_start = res['date_from']
        date_end =  res['date_to']
        location_outsource = res.location_id.id
        
#         date_start = datetime.strptime('2015-01-01', '%Y-%m-%d')
#         date_end = datetime.strptime('2015-12-31', '%Y-%m-%d')
#         location_outsource = 12
        
        sql_dk = '''SELECT product_id,name, code, sum(product_qty_in - product_qty_out) as qty_dk
                FROM  (SELECT sm.product_id,pt.name , pp.default_code as code,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_in,
                    0 AS product_qty_out
                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day',sm.date) < '%s'
                AND sm.state = 'done'
                --AND sp.location_type = 'outsource_out'
                AND sm.location_id <> %s
                AND sm.location_dest_id = %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code

                UNION ALL

                SELECT sm.product_id,pt.name , pp.default_code as code,
                    0 AS product_qty_in,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_out

                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day',sm.date) <'%s'
                AND sm.state = 'done'
                --AND sp.location_type = 'outsource_in'
                AND sm.location_id = %s
                AND sm.location_dest_id <> %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code) table_dk GROUP BY product_id,name ,code
                    ''' % (date_start, location_outsource,location_outsource, date_start, location_outsource,location_outsource)
        
        sql_in_tk = '''
            SELECT sm.product_id,pt.name , pp.default_code as code,
                    COALESCE(sum(sm.product_qty),0) AS qty_in_tk
                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day',sm.date) >= '%s'
                AND date_trunc('day',sm.date) <= '%s'
                AND sm.state = 'done'
                --AND sp.location_type = 'outsource_out'
                AND sm.location_id <> %s
                AND sm.location_dest_id = %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code
        '''% (date_start, date_end, location_outsource,location_outsource)

        sql_out_tk = '''
            SELECT sm.product_id,pt.name , pp.default_code as code,
                    COALESCE(sum(sm.product_qty),0) AS qty_out_tk
                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day',sm.date) >= '%s'
                AND date_trunc('day',sm.date) <= '%s'
                AND sm.state = 'done'
                --AND sp.location_type = 'outsource_out'
                AND sm.location_id = %s
                AND sm.location_dest_id <> %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code
        '''% (date_start, date_end, location_outsource,location_outsource)

        sql_ck = '''SELECT product_id,name, code, sum(product_qty_in - product_qty_out) as qty_ck
                FROM  (SELECT sm.product_id,pt.name , pp.default_code as code,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_in,
                    0 AS product_qty_out
                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day',sm.date) <= '%s'
                AND sm.state = 'done'
                --AND sp.location_type = 'outsource_out'
                AND sm.location_id <> %s
                AND sm.location_dest_id = %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code

                UNION ALL

                SELECT sm.product_id,pt.name , pp.default_code as code,
                    0 AS product_qty_in,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_out

                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day',sm.date) <='%s'
                AND sm.state = 'done'
                --AND sp.location_type = 'outsource_in'
                AND sm.location_id = %s
                AND sm.location_dest_id <> %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code) table_ck GROUP BY product_id,name ,code
                    ''' % (date_end, location_outsource,location_outsource, date_end, location_outsource,location_outsource)

        sql = '''
            CREATE OR REPLACE VIEW stock_inventory_report AS (
            SELECT ROW_NUMBER() OVER(ORDER BY table_ck.code DESC) AS id ,
                    table_ck.product_id, table_ck.name, table_ck.code,
                    COALESCE(sum(qty_dk),0) as qty_dk,
                    COALESCE(sum(qty_in_tk),0) as qty_in_tk,
                    COALESCE(sum(qty_out_tk),0) as qty_out_tk,
                    COALESCE(sum(qty_ck),0)  as qty_ck
            FROM  (%s) table_ck
                LEFT JOIN (%s) table_in_tk on table_ck.product_id = table_in_tk.product_id
                LEFT JOIN (%s) table_out_tk on table_ck.product_id = table_out_tk.product_id
                LEFT JOIN (%s) table_dk on table_ck.product_id = table_dk.product_id
                GROUP BY table_ck.product_id, table_ck.name, table_ck.code)
        ''' %(sql_ck,sql_in_tk, sql_out_tk, sql_dk)
        
        cr.execute(sql)
        
        return {
            'name': ('Stock Inventory Report'),
            'view_type': 'form',
            'view_mode': 'tree,graph',
            'res_model': 'stock.inventory.report',
            'type': 'ir.actions.act_window',
            'context': context,
        }
        
stock_inventory_wizard()
