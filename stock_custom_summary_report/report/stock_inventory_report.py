from odoo import api, models
from odoo.tools.misc import formatLang


class StockInventoryReport(models.AbstractModel):
    _name = 'report.stock_custom_summary_report.stock_report_template'

    @api.multi
    def render_html(self,docids, data=None):

        get_data = self.get_report_data(data)
        report_utility_pool = self.env['report.utility']
        op_unit_id = data['operating_unit_id']
        op_unit_obj = self.env['operating.unit'].search([('id', '=', op_unit_id)])
        data['address'] = report_utility_pool.getAddressByUnit(op_unit_obj)

        docargs = {
            'doc_ids': self._ids,
            'docs': self,
            'record': data,
            'lines': get_data['category'],
            'total': get_data['total'],
            'address': data['address'],
        }
        return self.env['report'].render('stock_custom_summary_report.stock_report_template', docargs)

    def get_report_data(self, data):
        date_from = data['date_from']
        date_start =date_from + ' 00:00:00'
        date_to = data['date_to']
        date_end = date_to + ' 23:59:59'
        location_outsource = data['location_id']
        category_id = data['category_id']
        product_id = data['product_id']
        cat_pool = self.env['product.category']
        product_pool = self.env['product.product']
        cat_lists = []

        sub_list = {
            'product': [],
            'sub-total': {
                'title': 'Sub Total',
                'total_dk_qty': 0,
                'total_dk_val': 0,
                'total_in_qty': 0,
                'total_in_val': 0,
                'total_out_qty': 0,
                'total_out_val': 0,
                'total_ck_qty': 0,
                'total_ck_val': 0,

            }
        }

        grand_total = {
            'title': 'GRAND TOTAL',
            'total_dk_qty': 0,
            'total_dk_val': 0,
            'total_in_qty': 0,
            'total_in_val': 0,
            'total_out_qty': 0,
            'total_out_val': 0,
            'total_ck_qty': 0,
            'total_ck_val': 0,
        }

        if category_id:
            categories = cat_pool.get_categories(category_id)
            category = {val.name: {
                'product': [],
                'sub-total': {
                    'title': 'SUB TOTAL',
                    'total_dk_qty': 0.0,
                    'total_dk_val': 0.0,
                    'total_in_qty': 0.0,
                    'total_in_val': 0.0,
                    'total_out_qty': 0.0,
                    'total_out_val': 0.0,
                    'total_ck_qty': 0.0,
                    'total_ck_val': 0.0,
                }
            } for val in cat_pool.search([('id', 'in', categories)])}
        else:
            cat_lists = cat_pool.search([], order='name ASC')
            category = {val.name: {
                'product': [],
                'sub-total': {
                    'title': 'SUB TOTAL',
                    'total_dk_qty': 0.0,
                    'total_dk_val': 0.0,
                    'total_in_qty': 0.0,
                    'total_in_val': 0.0,
                    'total_out_qty': 0.0,
                    'total_out_val': 0.0,
                    'total_ck_qty': 0.0,
                    'total_ck_val': 0.0,
                }
            } for val in cat_lists}

        if cat_lists:
            categories = cat_lists.ids
        # else:
        #     categories = cat_lists

        if len(categories) == 1:
            category_param = "(" + str(data['category_id']) + ")"
        else:
            category_param = str(tuple(categories))

        if product_id:
            product_param = "(" + str(data['product_id']) + ")"
        else:
            product_list = product_pool.search([('product_tmpl_id.categ_id.id', 'in', categories)])
            if len(product_list) == 1:
                product_param = "(" + str(product_list.id) + ")"
            elif len(product_list) > 1:
                product_param = str(tuple(product_list.ids))
            else:
                product_param = '(0)'

        sql_dk = '''
                 SELECT product_id,
                           name,
                           code,
                           uom_name,
                           category,
                           cost_val AS rate_dk,
                           ROUND(Sum(product_qty_in - product_qty_out), 4)                AS qty_dk,
                           ( cost_val * ROUND(Sum(product_qty_in - product_qty_out), 4) ) AS val_dk
                    FROM   (
                            SELECT sm.product_id,
                                    pt.name,
                                    pp.default_code AS code,
                                    pu.name AS uom_name,
                                    pc.name AS category,
                                    Coalesce(Sum(sm.product_qty), 0) AS product_qty_in,
                                    Coalesce((SELECT ph.current_price FROM   product_cost_price_history ph
                                              WHERE  Date_trunc('day', ph.modified_datetime+ interval'6h') < '%s'
                                              AND pp.id = ph.product_id
                                              ORDER  BY ph.modified_datetime DESC LIMIT  1), 0) AS cost_val,
                            0 AS product_qty_out
                            FROM stock_move sm  
                            LEFT JOIN stock_picking sp 
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
                            WHERE  sm.date + interval'6h' < '%s'
                                   AND sm.state = 'done'
                                   AND sm.location_id <> %s
                                   AND sm.location_dest_id = %s
                                   AND pc.id IN  %s
                                   AND pp.id IN %s
                            GROUP  BY sm.product_id,
                                      pt.name,pp.default_code,
                                      pp.id,
                                      pc.name,
                                      pu.name
                            UNION ALL
                            SELECT sm.product_id,
                                   pt.name,
                                   pp.default_code                  AS code,
                                   pu.name                          AS uom_name,
                                   pc.name         				    AS category,
                                   0                                AS product_qty_in,
                                   Coalesce((SELECT ph.current_price
                                             FROM   product_cost_price_history ph
                                             WHERE  Date_trunc('day', ph.modified_datetime + interval'6h') < '%s'
                                                    AND pp.id = ph.product_id
                                             ORDER  BY ph.modified_datetime DESC
                                             LIMIT  1), 0)          AS cost_val,
                                   Coalesce(Sum(sm.product_qty), 0) AS product_qty_out
                            FROM   stock_move sm
                                   LEFT JOIN stock_picking sp
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
                            WHERE  sm.date + interval'6h' < '%s'
                                   AND sm.state = 'done'
                                   AND sm.location_id = %s
                                   AND sm.location_dest_id <> %s
                                   AND pc.id IN  %s
                                   AND pp.id IN %s
                            GROUP  BY sm.product_id,
                                      pt.name,
                                      pp.default_code,
                                      pp.id,
                                      pc.name,
                                      pu.name
                            ) table_dk
                    GROUP  BY product_id,
                              name,
                              code,
                              cost_val,
                              uom_name,
                              category
                 
                 ''' % (date_start, date_start, location_outsource, location_outsource, category_param,product_param,
                        date_start, date_start, location_outsource, location_outsource, category_param,product_param)

        sql_in_tk = '''
                            SELECT product_id, 
                                   NAME, 
                                   code,
                                   uom_name, 
                                   category,
                                   cost_val AS rate_in,
                                   Sum(qty_in_tk) AS qty_in_tk, 
                                   Sum(val_in_tk) AS val_in_tk 
                            FROM   (SELECT sm.product_id, 
                                           pt.NAME, 
                                           pp.default_code                          AS code,
                                           pu.name                                  AS uom_name, 
                                           pc.name                                  AS category, 
                                           sm.product_qty                           AS qty_in_tk, 
                                           sm.product_qty * Coalesce((SELECT ph.current_price
                                             FROM   product_cost_price_history ph
                                             WHERE  ph.modified_datetime + interval'6h' <= '%s'
                                                    AND pp.id = ph.product_id
                                             ORDER  BY ph.modified_datetime DESC,ph.id DESC
                                             LIMIT  1), 0) AS val_in_tk,
                                           Coalesce((SELECT ph.current_price
                                             FROM   product_cost_price_history ph
                                             WHERE  ph.modified_datetime + interval'6h' <= '%s'
                                                    AND pp.id = ph.product_id
                                             ORDER  BY ph.modified_datetime DESC,ph.id DESC
                                             LIMIT  1), 0)          AS cost_val
                                    FROM   stock_move sm 
                                           LEFT JOIN stock_picking sp 
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
                                    WHERE  sm.date + interval'6h' BETWEEN '%s' AND '%s' 
                                           AND sm.state = 'done' 
                                           --AND sp.location_type = 'outsource_out' 
                                           AND sm.location_id <> %s
                                           AND sm.location_dest_id = %s 
                                           AND pc.id IN %s
                                           AND pp.id IN %s
                                   --AND usage like 'internal' 
                                   )t1 
                            GROUP  BY product_id, 
                                      NAME, 
                                      code,
                                      uom_name,
                                      category,
                                      cost_val 
                        ''' % (date_end,date_end,date_start, date_end, location_outsource, location_outsource, category_param,product_param)

        sql_out_tk = '''SELECT product_id,
                           name,
                           code,
                           uom_name,
                           category,
                           list_price AS rate_out,
                           Sum(qty_out_tk)              AS qty_out_tk,
                           Sum(val_out_tk)              AS val_out_tk
                    FROM   (SELECT sm.product_id,
                                   pt.name,
                                   pp.default_code         AS code,
                                   pu.name                 AS uom_name,
                                   pc.name                 AS category,
                                   sm.product_qty          AS qty_out_tk,
                                   Coalesce((SELECT ph.current_price
                                             FROM   product_cost_price_history ph
                                             WHERE  ph.modified_datetime + interval'6h' <= '%s'
                                                    AND pp.id = ph.product_id
                                             ORDER  BY ph.modified_datetime DESC,ph.id DESC
                                             LIMIT  1), 0) AS list_price,
                                   sm.product_qty * Coalesce((SELECT ph.current_price
                                             FROM   product_cost_price_history ph
                                             WHERE  ph.modified_datetime + interval'6h' <= '%s'
                                                    AND pp.id = ph.product_id
                                             ORDER  BY ph.modified_datetime DESC,ph.id DESC
                                             LIMIT  1), 0) AS val_out_tk
                            FROM   stock_move sm
                                   LEFT JOIN stock_picking sp
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
                            WHERE  sm.date + interval'6h' BETWEEN '%s' AND '%s'
                                   AND sm.state = 'done'
                                   AND sm.location_id = %s
                                   AND sm.location_dest_id <> %s
                                   AND pc.id IN %s
                                   AND pp.id IN %s
                           )t1
                    GROUP  BY product_id,
                              name,
                              code,
                              uom_name,
                              category,
                              list_price
                        ''' % (date_end,date_end,date_start, date_end, location_outsource, location_outsource, category_param,product_param)

        sql_ck = '''
                  SELECT product_id,
                   name,
                   code,
                   uom_name,
                   category,
                   cost_val AS rate_ck,
                   ROUND(Sum(product_qty_in - product_qty_out), 4)                AS qty_ck,
                   ( cost_val * ROUND(Sum(product_qty_in - product_qty_out), 4) ) AS val_ck
            FROM   (SELECT sm.product_id,
                           pt.name,
                           pp.default_code                  AS code,
                           pu.name                          AS uom_name,
                           pc.name                          AS category,
                           Coalesce(Sum(sm.product_qty), 0) AS product_qty_in,
                           Coalesce((SELECT ph.current_price
                                             FROM   product_cost_price_history ph
                                             WHERE  ph.modified_datetime + interval'6h' <= '%s'
                                                    AND pp.id = ph.product_id
                                             ORDER  BY ph.modified_datetime DESC,ph.id DESC
                                             LIMIT  1), 0)    AS cost_val,
                           0 AS product_qty_out
                    FROM   stock_move sm
                           LEFT JOIN stock_picking sp
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
                    WHERE  sm.date + interval'6h' <= '%s'
                           AND sm.state = 'done'
                           AND sm.location_id <> %s
                           AND sm.location_dest_id = %s
                           AND pc.id IN %s
                           AND pp.id IN %s
                    GROUP  BY sm.product_id,
                              pt.name,
                              pp.default_code,
                              pp.id,
                              pc.name,
                              pu.name
                    UNION ALL
                    SELECT sm.product_id,
                           pt.name,
                           pp.default_code                  AS code,
                           pu.name                          AS uom_name,
                           pc.name                          AS category,
                           0                                AS product_qty_in,
                           Coalesce((SELECT ph.current_price
                                     FROM   product_cost_price_history ph
                                     WHERE  ph.modified_datetime + interval'6h' <= '%s'
                                            AND pp.id = ph.product_id
                                     ORDER  BY ph.modified_datetime DESC,ph.id DESC
                                     LIMIT  1), 0)          AS cost_val,
                           Coalesce(Sum(sm.product_qty), 0) AS product_qty_out
                    FROM   stock_move sm
                           LEFT JOIN stock_picking sp
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
                    WHERE  sm.date + interval'6h' <= '%s'
                           AND sm.state = 'done'
                           AND sm.location_id = %s
                           AND sm.location_dest_id <> %s
                           AND pc.id IN %s
                           AND pp.id IN %s
                    GROUP  BY sm.product_id,
                              pt.name,
                              pp.default_code,
                              pp.id,
                              pc.name,
                              pu.name
                    ) table_ck
            GROUP  BY product_id,
                      name,
                      code,
                      uom_name,
                      category,
                      cost_val 
                        ''' % (date_end, date_end, location_outsource, location_outsource, category_param,product_param,
                               date_end, date_end, location_outsource, location_outsource, category_param,product_param)

        sql = '''
                            SELECT ROW_NUMBER() OVER(ORDER BY table_ck.code DESC) AS id ,
                                    table_ck.product_id, 
                                    table_ck.name, 
                                    table_ck.uom_name, 
                                    table_ck.code,
                                    table_ck.category, 
                                    COALESCE(table_dk.rate_dk,0) as rate_dk,
                                    COALESCE(table_in_tk.rate_in,0) as rate_in,
                                    COALESCE(table_out_tk.rate_out,0) as rate_out,
                                    COALESCE(table_ck.rate_ck,0) as rate_ck,
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
                                table_ck.uom_name,table_dk.rate_dk,table_in_tk.rate_in,table_out_tk.rate_out,table_ck.rate_ck

                        ''' % (sql_ck, sql_in_tk, sql_out_tk, sql_dk)

        self.env.cr.execute(sql)
        for vals in self.env.cr.dictfetchall():
            if vals:
                category[vals['category']]['product'].append(vals)

                total = category[vals['category']]['sub-total']
                total['name'] = vals['category']

                if total['total_in_val']:
                    total['total_in_val'] = float(total['total_in_val'].replace(',','')) + vals['val_in_tk']
                else:
                    total['total_in_val'] = total['total_in_val'] + vals['val_in_tk']

                if total['total_dk_val']:
                    total['total_dk_val'] = float(total['total_dk_val'].replace(',','')) + vals['val_dk']
                else:
                    total['total_dk_val'] = total['total_dk_val'] + vals['val_dk']

                if total['total_out_val']:
                    total['total_out_val'] = float(total['total_out_val'].replace(',','')) + vals['val_out_tk']
                else:
                    total['total_out_val'] = total['total_out_val'] + vals['val_out_tk']

                if total['total_ck_val']:
                    total['total_ck_val'] = float(total['total_ck_val'].replace(',','')) + vals['val_ck']
                else:
                    total['total_ck_val'] = total['total_ck_val'] + vals['val_ck']

                total['total_dk_qty'] = total['total_dk_qty'] + vals['qty_dk']
                total['total_in_qty'] = total['total_in_qty'] + vals['qty_in_tk']
                total['total_out_qty'] = total['total_out_qty'] + vals['qty_out_tk']
                total['total_ck_qty'] = total['total_ck_qty'] + vals['qty_ck']

                total['total_dk_val'] = formatLang(self.env, total['total_dk_val'])
                total['total_in_val'] = formatLang(self.env, total['total_in_val'])
                total['total_out_val'] = formatLang(self.env, total['total_out_val'])
                total['total_ck_val'] = formatLang(self.env, total['total_ck_val'])

                grand_total['total_dk_qty'] = grand_total['total_dk_qty'] + vals['qty_dk']
                grand_total['total_dk_val'] = grand_total['total_dk_val'] + vals['val_dk']
                grand_total['total_in_qty'] = grand_total['total_in_qty'] + vals['qty_in_tk']
                grand_total['total_in_val'] = grand_total['total_in_val'] + vals['val_in_tk']
                grand_total['total_out_qty'] = grand_total['total_out_qty'] + vals['qty_out_tk']
                grand_total['total_out_val'] = grand_total['total_out_val'] + vals['val_out_tk']
                grand_total['total_ck_qty'] = grand_total['total_ck_qty'] + vals['qty_ck']
                grand_total['total_ck_val'] = grand_total['total_ck_val'] + vals['val_ck']

                vals['val_dk'] = formatLang(self.env, vals['val_dk'])
                vals['val_in_tk'] = formatLang(self.env, vals['val_in_tk'])
                vals['val_out_tk'] = formatLang(self.env, vals['val_out_tk'])
                vals['val_ck'] = formatLang(self.env, vals['val_ck'])

                vals['rate_dk'] = formatLang(self.env, vals['rate_dk'])
                vals['rate_in'] = formatLang(self.env, vals['rate_in'])
                vals['rate_out'] = formatLang(self.env, vals['rate_out'])
                vals['rate_ck'] = formatLang(self.env, vals['rate_ck'])


        grand_total['total_dk_val'] = formatLang(self.env,grand_total['total_dk_val'])
        grand_total['total_in_val'] = formatLang(self.env,grand_total['total_in_val'])
        grand_total['total_out_val'] = formatLang(self.env,grand_total['total_out_val'])
        grand_total['total_ck_val'] = formatLang(self.env,grand_total['total_ck_val'])
        return {'category': category, 'total': grand_total}
