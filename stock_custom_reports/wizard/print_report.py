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

from openerp import api, exceptions, fields, models
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval
import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round
from openerp import tools
# from openerp.exceptions import UserError
import time

class StockInventoryWizard(models.TransientModel):

    _name = 'stock.inventory.wizard'

    date_from= fields.Date("Date from", required=True)
    date_to= fields.Date("Date to", required=True)
    location_id= fields.Many2one('stock.location', 'Location', required=True)
    
    _defaults = {
               'date_from': lambda *a: time.strftime('%Y-%m-%d'),
               'date_to': lambda *a: time.strftime('%Y-%m-%d'),
               }
    
    @api.multi
    def print_report(self):
        context = self.env.context
        datas = {'ids': context.get('active_ids', [])}

        res = self.browse(self._ids)
        res = res and res[0] or {}
        ctx = {} 
#         ctx = context.copy()
        ctx['date_from'] = res['date_from']
        ctx['date_to'] = res['date_to']
#         ctx['location_id'] = res['location_id']
        
        tools.drop_view_if_exists(self.env.cr,'stock_inventory_report')
        date_start = res['date_from']
        date_end =  res['date_to']
        location_outsource = res.location_id.id
        ctx['form'] = self.read([], ['date_from', 'date_to'])[0]
#         date_start = datetime.strptime('2015-01-01', '%Y-%m-%d')
#         date_end = datetime.strptime('2015-12-31', '%Y-%m-%d')
#         location_outsource = 12
        
        
        sql_dk = '''SELECT product_id,name, code, sum(product_qty_in - product_qty_out) as qty_dk,cost_val, (cost_val*sum(product_qty_in - product_qty_out)) as val_dk
                FROM  (SELECT sm.product_id,pt.name , pp.default_code as code,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_in,
                    COALESCE((Select ph.cost from product_price_history ph where date_trunc('day',ph.datetime)<'%s' AND pp.id = ph.product_id
                        order by ph.datetime desc limit 1),0)
                        AS cost_val,
                    0 AS product_qty_out
                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pp.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                
                WHERE date_trunc('day',sm.date) < '%s'
                AND sm.state = 'done'
                --AND sp.location_type = 'outsource_out'
                AND sm.location_id <> %s
                AND sm.location_dest_id = %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code,
                pp.id

                UNION ALL

                SELECT sm.product_id,pt.name , pp.default_code as code,
                    0 AS product_qty_in,
                    COALESCE((Select ph.cost from product_price_history ph where date_trunc('day',ph.datetime)<'%s' AND pp.id = ph.product_id
                        order by ph.datetime desc limit 1),0)
                        AS cost_val,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_out
                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pp.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                
                WHERE date_trunc('day',sm.date) <'%s'
                AND sm.state = 'done'
                --AND sp.location_type = 'outsource_in'
                AND sm.location_id = %s
                AND sm.location_dest_id <> %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code,
                pp.id
                
                UNION ALL

            SELECT sm.product_id,pt.name , pp.default_code as code,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_in,
                    COALESCE((Select ph.cost from product_price_history ph where date_trunc('day',ph.datetime)<'%s' AND pp.id = ph.product_id
                        order by ph.datetime desc limit 1),0)
                        AS cost_val,
                    0 AS product_qty_out
                FROM stock_move sm
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pp.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                
                WHERE date_trunc('day',sm.date) < '%s'
                AND sm.state = 'done'
                AND sm.location_id <> %s
                AND sm.location_dest_id = %s
                AND sm.picking_id is null
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code,
                pp.id
                
                ) table_dk GROUP BY product_id,name ,code, cost_val
                ''' % (date_start, date_start, location_outsource,location_outsource, date_start, date_start,location_outsource,location_outsource,date_start,date_start, location_outsource,location_outsource)
        print '-----sql_dk---',sql_dk
        
        sql_in_tk = '''
            select product_id,name,code, sum(qty_in_tk) as qty_in_tk,sum(val_in_tk) as val_in_tk 
                from (SELECT sm.product_id,pt.name , pp.default_code as code,
                    sm.product_qty AS qty_in_tk, sm.product_qty*COALESCE(price_unit,0) AS val_in_tk
                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pp.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                    WHERE date_trunc('day',sm.date) between '%s' and '%s'
                    AND sm.state = 'done'
                    --AND sp.location_type = 'outsource_out'
                    AND sm.location_id <> %s
                    AND sm.location_dest_id = %s
                    --AND usage like 'internal'
                    )t1
            GROUP BY product_id,name,code
        '''% (date_start, date_end, location_outsource,location_outsource)
        print '-----sql_in_tk---',sql_in_tk
        sql_out_tk = '''
            select product_id,name,code, sum(qty_out_tk) as qty_out_tk,
                sum(qty_out_tk)*val_out_tk AS val_out_tk
                from (SELECT sm.product_id,pt.name , pp.default_code as code,
                                sm.product_qty AS qty_out_tk,
                                COALESCE((Select ph.cost from product_price_history ph where date_trunc('day',ph.datetime)<='%s' AND pp.id = ph.product_id
                        order by ph.datetime desc limit 1),0)
                        AS val_out_tk
                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pp.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day',sm.date) between '%s' and '%s'
                AND sm.state = 'done'
                --AND sp.location_type = 'outsource_out'
                AND sm.location_id = %s
                AND sm.location_dest_id <> %s
                --AND usage like 'internal'
                )t1
            GROUP BY product_id,name,code,val_out_tk
        '''% (date_end, date_start, date_end, location_outsource,location_outsource)
        print '-----sql_out_tk---',sql_out_tk

        sql_ck = '''SELECT product_id,name, code, sum(product_qty_in - product_qty_out) as qty_ck, (cost_val*sum(product_qty_in - product_qty_out)) as val_ck
                FROM  (SELECT sm.product_id,pt.name , pp.default_code as code,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_in,
                    COALESCE((Select ph.cost from product_price_history ph where date_trunc('day',ph.datetime)<='%s' AND pp.id = ph.product_id
                        order by ph.datetime desc limit 1),0)
                        AS cost_val,
                    0 AS product_qty_out
                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pp.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day',sm.date) <= '%s'
                AND sm.state = 'done'
                --AND sp.location_type = 'outsource_out'
                AND sm.location_id <> %s
                AND sm.location_dest_id = %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code,
                pp.id

                UNION ALL

                SELECT sm.product_id,pt.name , pp.default_code as code,
                    0 AS product_qty_in,
                    COALESCE((Select ph.cost from product_price_history ph where date_trunc('day',ph.datetime)<='%s' AND pp.id = ph.product_id
                        order by ph.datetime desc limit 1),0)
                        AS cost_val,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_out
                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pp.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day',sm.date) <='%s'
                AND sm.state = 'done'
                --AND sp.location_type = 'outsource_in'
                AND sm.location_id = %s
                AND sm.location_dest_id <> %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code,
                pp.id
                
                UNION ALL

            SELECT sm.product_id,pt.name , pp.default_code as code,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_in,
                    COALESCE((Select ph.cost from product_price_history ph where date_trunc('day',ph.datetime)<='%s' AND pp.id = ph.product_id
                        order by ph.datetime desc limit 1),0)
                        AS cost_val,
                    0 AS product_qty_out
                FROM stock_move sm
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pp.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day',sm.date) <= '%s'
                AND sm.state = 'done'
                AND sm.location_id <> %s
                AND sm.location_dest_id = %s
                AND sm.picking_id is null
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code,
                pp.id
                ) table_ck GROUP BY product_id,name ,code,cost_val
                    ''' % (date_end,date_end, location_outsource,location_outsource, date_end, date_end, location_outsource,location_outsource, date_end, date_end, location_outsource,location_outsource)
        print '-----sql_ck---',sql_ck        
        sql = '''
            CREATE OR REPLACE VIEW stock_inventory_report AS (
            SELECT ROW_NUMBER() OVER(ORDER BY table_ck.code DESC) AS id ,
                    table_ck.product_id, table_ck.name, table_ck.code,
                    COALESCE(sum(qty_dk),0) as qty_dk,
                    COALESCE(sum(qty_in_tk),0) as qty_in_tk,
                    COALESCE(sum(qty_out_tk),0) as qty_out_tk,
                    COALESCE(sum(qty_ck),0)  as qty_ck,
                    COALESCE(sum(val_dk),0) as val_dk,
                    COALESCE(sum(val_in_tk),0) as val_in_tk,
                    COALESCE(sum(val_out_tk),0) as val_out_tk,
                    COALESCE(sum(val_ck),0)  as val_ck
            FROM  (%s) table_ck
                LEFT JOIN (%s) table_in_tk on table_ck.product_id = table_in_tk.product_id
                LEFT JOIN (%s) table_out_tk on table_ck.product_id = table_out_tk.product_id
                LEFT JOIN (%s) table_dk on table_ck.product_id = table_dk.product_id
                GROUP BY table_ck.product_id, table_ck.name, table_ck.code)
        ''' %(sql_ck,sql_in_tk, sql_out_tk, sql_dk)
        
        self.env.cr.execute(sql)
        
        return {
            'name': ('Stock Inventory Report'),
            'view_type': 'form',
            'view_mode': 'tree,graph',
            'res_model': 'stock.inventory.report',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'data':ctx
            
        }
        
StockInventoryWizard()
