from datetime import datetime

from openerp import api, models


class StockInventoryReport(models.AbstractModel):
    _name = 'report.category_stock_summary_reports.stock_inventory_report_qweb'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'category_stock_summary_reports.stock_inventory_report_qweb')

        get_data = self.get_report_data(data)

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'record': data,
            'total': 0,
            'lines': get_data


        }
        return report_obj.render('category_stock_summary_reports.stock_inventory_report_qweb', docargs)

    def get_report_data(self, data):
        date_start = data['date_from']
        date_end = data['date_to']
        location_outsource = data['shop_id']
        category_id = data['category_id']
        cat_pool = self.env['product.category']

        if category_id:
            categories = cat_pool.get_categories(category_id)
            category = {val.name: [] for val in cat_pool.search([('id','=',data['category_id'])])}
        else:
            categories = cat_pool.search([],order='name ASC')
            category = {val.name: [] for val in categories}


        if len(categories) == 1:
            category_param = "(" + str(data['category_id']) + ")"
        else:
            category_param = str(tuple(categories.ids))

        sql_dk = '''SELECT product_id, 
                           name, 
                           code,
                           uom_name,
                           category, 
                           Sum(product_qty_in - product_qty_out)                AS qty_dk, 
                           cost_val, 
                           ( cost_val * Sum(product_qty_in - product_qty_out) ) AS val_dk 
                    FROM   (SELECT sm.product_id, 
                                   pt.name, 
                                   pp.default_code                  AS code,
                                   pu.name                          AS uom_name,
                                   pc.name				            AS category, 
                                   Coalesce(Sum(sm.product_qty), 0) AS product_qty_in, 
                                   Coalesce((SELECT ph.cost 
                                             FROM   product_price_history ph 
                                             WHERE  Date_trunc('day', ph.datetime) < '%s' 
                                                    AND pt.id = ph.product_template_id 
                                             ORDER  BY ph.datetime DESC 
                                             LIMIT  1), 0)          AS cost_val, 
                                   0                                AS product_qty_out 
                            FROM   stock_picking sp 
                                   LEFT JOIN stock_move sm 
                                          ON sm.picking_id = sp.id 
                                   LEFT JOIN product_product pp 
                                          ON sm.product_id = pp.id 
                                   LEFT JOIN product_template pt 
                                          ON pp.product_tmpl_id = pt.id 
                                   LEFT JOIN stock_location sl 
                                          ON sm.location_id = sl.id 
                                   LEFT JOIN product_category pc 
                                          ON pt.categ_id = pc.id
                                   LEFT JOIN product_uom pu 
				                          ON( pu.id = pt.uom_id ) 
                            WHERE  Date_trunc('day', sm.date) < '%s' 
                                   AND sm.state = 'done' 
                                   --AND sp.location_type = 'outsource_out' 
                                   AND sm.location_id <> %s
                                   AND sm.location_dest_id = %s
                                   AND pc.id IN %s
                            --AND usage like 'internal' 
                            GROUP  BY sm.product_id, 
                                      pt.name, 
                                      pp.default_code, 
                                      pt.id,
                                      pc.name,
                                      pu.name 
                            UNION ALL 
                            SELECT sm.product_id, 
                                   pt.name, 
                                   pp.default_code                  AS code,
                                   pu.name                          AS uom_name,
                                   pc.name         				    AS category, 
                                   0                                AS product_qty_in, 
                                   Coalesce((SELECT ph.cost 
                                             FROM   product_price_history ph 
                                             WHERE  Date_trunc('day', ph.datetime) < '%s' 
                                                    AND pt.id = ph.product_template_id 
                                             ORDER  BY ph.datetime DESC 
                                             LIMIT  1), 0)          AS cost_val, 
                                   Coalesce(Sum(sm.product_qty), 0) AS product_qty_out 
                            FROM   stock_picking sp 
                                   LEFT JOIN stock_move sm 
                                          ON sm.picking_id = sp.id 
                                   LEFT JOIN product_product pp 
                                          ON sm.product_id = pp.id 
                                   LEFT JOIN product_template pt 
                                          ON pp.product_tmpl_id = pt.id 
                                   LEFT JOIN stock_location sl 
                                          ON sm.location_id = sl.id 
                                   LEFT JOIN product_category pc 
                                          ON pt.categ_id = pc.id 
                                   LEFT JOIN product_uom pu 
				                          ON( pu.id = pt.uom_id ) 
                            WHERE  Date_trunc('day', sm.date) < '%s' 
                                   AND sm.state = 'done' 
                                   --AND sp.location_type = 'outsource_in' 
                                   AND sm.location_id = %s
                                   AND sm.location_dest_id <> %s
                                   AND pc.id IN %s
                            --AND usage like 'internal' 
                            GROUP  BY sm.product_id, 
                                      pt.name, 
                                      pp.default_code, 
                                      pt.id,
                                      pc.name,
                                      pu.name 
                            UNION ALL 
                            SELECT sm.product_id, 
                                   pt.name, 
                                   pp.default_code                  AS code,
                                   pu.name                          AS uom_name, 
                                   pc.name				            AS category,
                                   Coalesce(Sum(sm.product_qty), 0) AS product_qty_in, 
                                   Coalesce((SELECT ph.cost 
                                             FROM   product_price_history ph 
                                             WHERE  Date_trunc('day', ph.datetime) < '%s' 
                                                    AND pt.id = ph.product_template_id 
                                             ORDER  BY ph.datetime DESC 
                                             LIMIT  1), 0)          AS cost_val, 
                                   0                                AS product_qty_out 
                            FROM   stock_move sm 
                                   LEFT JOIN product_product pp 
                                          ON sm.product_id = pp.id 
                                   LEFT JOIN product_template pt 
                                          ON pp.product_tmpl_id = pt.id 
                                   LEFT JOIN stock_location sl 
                                          ON sm.location_id = sl.id 
                                   LEFT JOIN product_category pc 
                                          ON pt.categ_id = pc.id
                                   LEFT JOIN product_uom pu 
				                          ON( pu.id = pt.uom_id )  
                            WHERE  Date_trunc('day', sm.date) < '%s' 
                                   AND sm.state = 'done' 
                                   AND sm.location_id <> %s
                                   AND sm.location_dest_id = %s 
                                   AND sm.picking_id IS NULL 
                                   AND pc.id IN %s
                            GROUP  BY sm.product_id, 
                                      pt.name, 
                                      pp.default_code, 
                                      pt.id,
                                      pc.name,
                                      pu.name) table_dk 
                    GROUP  BY product_id, 
                              name, 
                              code, 
                              cost_val,
                              uom_name,
                              category 
              ''' % (date_start, date_start, location_outsource, location_outsource, category_param,
                                       date_start, date_start, location_outsource, location_outsource, category_param,
                                       date_start, date_start, location_outsource, location_outsource, category_param)

        sql_in_tk = '''
                    SELECT product_id, 
                           NAME, 
                           code,
                           uom_name, 
                           category,
                           Sum(qty_in_tk) AS qty_in_tk, 
                           Sum(val_in_tk) AS val_in_tk 
                    FROM   (SELECT sm.product_id, 
                                   pt.NAME, 
                                   pp.default_code                          AS code,
                                   pu.name                                  AS uom_name, 
                                   pc.name                                  AS category, 
                                   sm.product_qty                           AS qty_in_tk, 
                                   sm.product_qty * COALESCE(price_unit, 0) AS val_in_tk 
                            FROM   stock_picking sp 
                                   LEFT JOIN stock_move sm 
                                          ON sm.picking_id = sp.id 
                                   LEFT JOIN product_product pp 
                                          ON sm.product_id = pp.id 
                                   LEFT JOIN product_template pt 
                                          ON pp.product_tmpl_id = pt.id 
                                   LEFT JOIN stock_location sl 
                                          ON sm.location_id = sl.id 
                                   LEFT JOIN product_category pc 
                                          ON pt.categ_id = pc.id
                                   LEFT JOIN product_uom pu 
				                          ON( pu.id = pt.uom_id )  
                            WHERE  Date_trunc('day', sm.date) BETWEEN '%s' AND '%s' 
                                   AND sm.state = 'done' 
                                   --AND sp.location_type = 'outsource_out' 
                                   AND sm.location_id <> %s
                                   AND sm.location_dest_id = %s 
                                   AND pc.id IN %s
                           --AND usage like 'internal' 
                           )t1 
                    GROUP  BY product_id, 
                              NAME, 
                              code,
                              uom_name,
                              category 
                ''' % (date_start, date_end, location_outsource, location_outsource, category_param)

        sql_out_tk = '''
                    SELECT product_id, 
                           name, 
                           code,
                           uom_name,
                           category, 
                           Sum(qty_out_tk)              AS qty_out_tk, 
                           Sum(qty_out_tk) * val_out_tk AS val_out_tk 
                    FROM   (SELECT sm.product_id, 
                                   pt.name, 
                                   pp.default_code         AS code,
                                   pu.name                 AS uom_name,
                                   pc.name                 AS category, 
                                   sm.product_qty          AS qty_out_tk, 
                                   Coalesce((SELECT ph.cost 
                                             FROM   product_price_history ph 
                                             WHERE  Date_trunc('day', ph.datetime) <= '%s' 
                                                    AND pt.id = ph.product_template_id 
                                             ORDER  BY ph.datetime DESC 
                                             LIMIT  1), 0) AS val_out_tk 
                            FROM   stock_picking sp 
                                   LEFT JOIN stock_move sm 
                                          ON sm.picking_id = sp.id 
                                   LEFT JOIN product_product pp 
                                          ON sm.product_id = pp.id 
                                   LEFT JOIN product_template pt 
                                          ON pp.product_tmpl_id = pt.id 
                                   LEFT JOIN stock_location sl 
                                          ON sm.location_id = sl.id 
                                   LEFT JOIN product_category pc 
                                          ON pt.categ_id = pc.id
                                   LEFT JOIN product_uom pu 
				                          ON( pu.id = pt.uom_id )  
                            WHERE  Date_trunc('day', sm.date) BETWEEN '%s' AND '%s' 
                                   AND sm.state = 'done' 
                                   --AND sp.location_type = 'outsource_out' 
                                   AND sm.location_id = %s
                                   AND sm.location_dest_id <> %s 
                                   AND pc.id IN %s 
                           --AND usage like 'internal' 
                           )t1 
                    GROUP  BY product_id, 
                              name, 
                              code, 
                              uom_name,
                              category,
                              val_out_tk 
                ''' % (date_end, date_start, date_end, location_outsource, location_outsource, category_param)

        sql_ck = '''
                    SELECT product_id, 
           name, 
           code,
           uom_name,
           category, 
           Sum(product_qty_in - product_qty_out)                AS qty_ck, 
           ( cost_val * Sum(product_qty_in - product_qty_out) ) AS val_ck 
    FROM   (SELECT sm.product_id, 
                   pt.name, 
                   pp.default_code                  AS code,
                   pu.name                          AS uom_name,
                   pc.name                          AS category, 
                   Coalesce(Sum(sm.product_qty), 0) AS product_qty_in, 
                   Coalesce((SELECT ph.cost 
                             FROM   product_price_history ph 
                             WHERE  Date_trunc('day', ph.datetime) <= '%s' 
                                    AND pt.id = ph.product_template_id 
                             ORDER  BY ph.datetime DESC 
                             LIMIT  1), 0)          AS cost_val, 
                   0                                AS product_qty_out 
            FROM   stock_picking sp 
                   LEFT JOIN stock_move sm 
                          ON sm.picking_id = sp.id 
                   LEFT JOIN product_product pp 
                          ON sm.product_id = pp.id 
                   LEFT JOIN product_template pt 
                          ON pp.product_tmpl_id = pt.id 
                   LEFT JOIN stock_location sl 
                          ON sm.location_id = sl.id 
                   LEFT JOIN product_category pc 
                          ON pt.categ_id = pc.id
                   LEFT JOIN product_uom pu 
                          ON( pu.id = pt.uom_id )  
            WHERE  Date_trunc('day', sm.date) <= '%s' 
                   AND sm.state = 'done' 
                   --AND sp.location_type = 'outsource_out' 
                   AND sm.location_id <> %s 
                   AND sm.location_dest_id = %s 
                   AND pc.id IN %s 
            --AND usage like 'internal' 
            GROUP  BY sm.product_id, 
                      pt.name, 
                      pp.default_code, 
                      pt.id,
                      pc.name,
                      pu.name 
            UNION ALL 
            SELECT sm.product_id, 
                   pt.name, 
                   pp.default_code                  AS code,
                   pu.name                          AS uom_name,
                   pc.name                          AS category, 
                   0                                AS product_qty_in, 
                   Coalesce((SELECT ph.cost 
                             FROM   product_price_history ph 
                             WHERE  Date_trunc('day', ph.datetime) <= '%s' 
                                    AND pt.id = ph.product_template_id 
                             ORDER  BY ph.datetime DESC 
                             LIMIT  1), 0)          AS cost_val, 
                   Coalesce(Sum(sm.product_qty), 0) AS product_qty_out 
            FROM   stock_picking sp 
                   LEFT JOIN stock_move sm 
                          ON sm.picking_id = sp.id 
                   LEFT JOIN product_product pp 
                          ON sm.product_id = pp.id 
                   LEFT JOIN product_template pt 
                          ON pp.product_tmpl_id = pt.id 
                   LEFT JOIN stock_location sl 
                          ON sm.location_id = sl.id 
                   LEFT JOIN product_category pc 
                          ON pt.categ_id = pc.id
                   LEFT JOIN product_uom pu 
                          ON( pu.id = pt.uom_id )   
            WHERE  Date_trunc('day', sm.date) <= '%s' 
                   AND sm.state = 'done' 
                   --AND sp.location_type = 'outsource_in' 
                   AND sm.location_id = %s
                   AND sm.location_dest_id <> %s
                   AND pc.id IN %s 
            --AND usage like 'internal' 
            GROUP  BY sm.product_id, 
                      pt.name, 
                      pp.default_code, 
                      pt.id,
                      pc.name,
                      pu.name 
            UNION ALL 
            SELECT sm.product_id, 
                   pt.name, 
                   pp.default_code                  AS code,
                   pu.name                          AS uom_name,
                   pc.name                          AS category, 
                   Coalesce(Sum(sm.product_qty), 0) AS product_qty_in, 
                   Coalesce((SELECT ph.cost 
                             FROM   product_price_history ph 
                             WHERE  Date_trunc('day', ph.datetime) <= '%s' 
                                    AND pt.id = ph.product_template_id 
                             ORDER  BY ph.datetime DESC 
                             LIMIT  1), 0)          AS cost_val, 
                   0                                AS product_qty_out 
            FROM   stock_move sm 
                   LEFT JOIN product_product pp 
                          ON sm.product_id = pp.id 
                   LEFT JOIN product_template pt 
                          ON pp.product_tmpl_id = pt.id 
                   LEFT JOIN stock_location sl 
                          ON sm.location_id = sl.id 
                   LEFT JOIN product_category pc 
                          ON pt.categ_id = pc.id
                   LEFT JOIN product_uom pu 
                          ON( pu.id = pt.uom_id )   
            WHERE  Date_trunc('day', sm.date) <= '%s' 
                   AND sm.state = 'done' 
                   AND sm.location_id <> %s
                   AND sm.location_dest_id = %s
                   AND pc.id IN %s 
                   AND sm.picking_id IS NULL 
            GROUP  BY sm.product_id, 
                      pt.name, 
                      pp.default_code, 
                      pt.id,
                      pc.name,
                      pu.name) table_ck 
    GROUP  BY product_id, 
              name, 
              code,
              uom_name,
              category, 
              cost_val  
                ''' % (date_end, date_end, location_outsource, location_outsource, category_param,
                                   date_end, date_end, location_outsource, location_outsource, category_param,
                                   date_end, date_end, location_outsource, location_outsource, category_param)

        sql_uom = '''SELECT pu.name as uom_name, 
                           pp.default_code, 
                           pp.id AS product_id 
                    FROM   product_template pt 
                           LEFT JOIN product_product pp 
                                  ON( pp.product_tmpl_id = pt.id ) 
                           LEFT JOIN product_uom pu 
                                  ON( pu.id = pt.uom_id )'''


        sql = '''
                    SELECT ROW_NUMBER() OVER(ORDER BY table_ck.code DESC) AS id ,
                            table_ck.product_id, table_ck.name, table_ck.uom_name, table_ck.code,
                            table_ck.category,
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
                        GROUP BY table_ck.product_id, table_ck.name, table_ck.code,table_ck.category,
                        table_ck.uom_name
                        
                ''' % (sql_ck, sql_in_tk, sql_out_tk, sql_dk)

        self.env.cr.execute(sql)
        for vals in self.env.cr.dictfetchall():
            category[vals['category']].append(vals)

        return category

