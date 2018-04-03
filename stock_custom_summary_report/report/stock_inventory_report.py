from datetime import datetime

from openerp import api, models


class StockInventoryReport(models.AbstractModel):
    _name = 'report.stock_custom_summary_report.stock_report_template'

    @api.multi
    def render_html(self,docids, data=None):

        # get_data = self.get_report_data(data)

        docargs = {
            'doc_ids': self._ids,
            # 'doc_model': report.model,
            'docs': self,
            'record': data,
            # 'lines': get_data['category'],
            # 'total': get_data['total'],

        }
        return self.env['report'].render('stock_custom_summary_report.stock_report_template', docargs)

    # def get_report_data(self, data):
    #     date_start = data['date_from']
    #     date_end = data['date_to']
    #     location_outsource = data['shop_id']
    #     category_id = data['category_id']
    #     cat_pool = self.env['product.category']
    #
    #     sub_list = {
    #         'product': [],
    #         'sub-total': {
    #             'title': 'Sub Total',
    #             'total_dk_qty': 0,
    #             'total_dk_val': 0,
    #             'total_in_qty': 0,
    #             'total_in_val': 0,
    #             'total_out_qty': 0,
    #             'total_out_val': 0,
    #             'total_ck_qty': 0,
    #             'total_ck_val': 0,
    #         }
    #     }
    # grand_total = {
    #         'title': 'GRAND TOTAL',
    #         'total_dk_qty': 0,
    #         'total_dk_val': 0,
    #         'total_in_qty': 0,
    #         'total_in_val': 0,
    #         'total_out_qty': 0,
    #         'total_out_val': 0,
    #         'total_ck_qty': 0,
    #         'total_ck_val': 0,
    #     }
    #
    #     if category_id:
    #         categories = cat_pool.get_categories(category_id)
    #         category = {val.name: {
    #             'product': [],
    #             'sub-total': {
    #                 'title': 'SUB TOTAL',
    #                 'total_dk_qty': 0.0,
    #                 'total_dk_val': 0.0,
    #                 'total_in_qty': 0.0,
    #                 'total_in_val': 0.0,
    #                 'total_out_qty': 0.0,
    #                 'total_out_val': 0.0,
    #                 'total_ck_qty': 0.0,
    #                 'total_ck_val': 0.0,
    #             }
    #         } for val in cat_pool.search([('id', 'in', categories)])}
    #     else:
    #         cat_lists = cat_pool.search([], order='name ASC')
    #         category = {val.name: {
    #             'product': [],
    #             'sub-total': {
    #                 'title': 'SUB TOTAL',
    #                 'total_dk_qty': 0.0,
    #                 'total_dk_val': 0.0,
    #                 'total_in_qty': 0.0,
    #                 'total_in_val': 0.0,
    #                 'total_out_qty': 0.0,
    #                 'total_out_val': 0.0,
    #                 'total_ck_qty': 0.0,
    #                 'total_ck_val': 0.0,
    #             }
    #         } for val in cat_lists}
    #
    #         if cat_lists:
    #             categories = cat_lists.ids
    #         else:
    #             categories = cat_lists
    #
    #     if len(categories) == 1:
    #         category_param = "(" + str(data['category_id']) + ")"
    #     else:
    #         category_param = str(tuple(categories))
    #
    #     sql_dk = '''SELECT product_id,
    #                        name,
    #                        code,
    #                        uom_name,
    #                        category,
    #                        cost_val AS rate_dk,
    #                        Sum(product_qty_in - product_qty_out)                AS qty_dk,
    #                        ( cost_val * Sum(product_qty_in - product_qty_out) ) AS val_dk
    #                 FROM   (SELECT sm.product_id,
    #                                pt.name,
    #                                pp.default_code                  AS code,
    #                                pu.name                          AS uom_name,
    #                                pc.name				            AS category,
    #                                Coalesce(Sum(sm.product_qty), 0) AS product_qty_in,
    #                                Coalesce((SELECT ph.cost
    #                                          FROM   product_price_history ph
    #                                          WHERE  Date_trunc('day', ph.datetime) < '%s'
    #                                                 AND pt.id = ph.product_template_id
    #                                          ORDER  BY ph.datetime DESC
    #                                          LIMIT  1), 0)          AS cost_val,
    #                                0                                AS product_qty_out
    #                         FROM   stock_picking sp
    #                                LEFT JOIN stock_move sm
    #                                       ON sm.picking_id = sp.id
    #                                LEFT JOIN product_product pp
    #                                       ON sm.product_id = pp.id
    #                                LEFT JOIN product_template pt
    #                                       ON pp.product_tmpl_id = pt.id
    #                                LEFT JOIN stock_location sl
    #                                       ON sm.location_id = sl.id
    #                                LEFT JOIN product_category pc
    #                                       ON pt.categ_id = pc.id
    #                                LEFT JOIN product_uom pu
		# 		                          ON( pu.id = pt.uom_id )
    #                         WHERE  Date_trunc('day', sm.date) < '%s'
    #                                AND sm.state = 'done'
    #                                --AND sp.location_type = 'outsource_out'
    #                                AND sm.location_id <> %s
    #                                AND sm.location_dest_id = %s
    #                                AND pc.id IN %s
    #                         --AND usage like 'internal'
    #                         GROUP  BY sm.product_id,
    #                                   pt.name,
    #                                   pp.default_code,
    #                                   pt.id,
    #                                   pc.name,
    #                                   pu.name
    #                         UNION ALL
    #                         SELECT sm.product_id,
    #                                pt.name,
    #                                pp.default_code                  AS code,
    #                                pu.name                          AS uom_name,
    #                                pc.name         				    AS category,
    #                                0                                AS product_qty_in,
    #                                Coalesce((SELECT ph.cost
    #                                          FROM   product_price_history ph
    #                                          WHERE  Date_trunc('day', ph.datetime) < '%s'
    #                                                 AND pt.id = ph.product_template_id
    #                                          ORDER  BY ph.datetime DESC
    #                                          LIMIT  1), 0)          AS cost_val,
    #                                Coalesce(Sum(sm.product_qty), 0) AS product_qty_out
    #                         FROM   stock_picking sp
    #                                LEFT JOIN stock_move sm
    #                                       ON sm.picking_id = sp.id
    #                                LEFT JOIN product_product pp
    #                                       ON sm.product_id = pp.id
    #                                LEFT JOIN product_template pt
    #                                       ON pp.product_tmpl_id = pt.id
    #                                LEFT JOIN stock_location sl
    #                                       ON sm.location_id = sl.id
    #                                LEFT JOIN product_category pc
    #                                       ON pt.categ_id = pc.id
    #                                LEFT JOIN product_uom pu
		# 		                          ON( pu.id = pt.uom_id )
    #                         WHERE  Date_trunc('day', sm.date) < '%s'
    #                                AND sm.state = 'done'
    #                                --AND sp.location_type = 'outsource_in'
    #                                AND sm.location_id = %s
    #                                AND sm.location_dest_id <> %s
    #                                AND pc.id IN %s
    #                         --AND usage like 'internal'
    #                         GROUP  BY sm.product_id,
    #                                   pt.name,
    #                                   pp.default_code,
    #                                   pt.id,
    #                                   pc.name,
    #                                   pu.name
    #                         UNION ALL
    #                         SELECT sm.product_id,
    #                                pt.name,
    #                                pp.default_code                  AS code,
    #                                pu.name                          AS uom_name,
    #                                pc.name				            AS category,
    #                                Coalesce(Sum(sm.product_qty), 0) AS product_qty_in,
    #                                Coalesce((SELECT ph.cost
    #                                          FROM   product_price_history ph
    #                                          WHERE  Date_trunc('day', ph.datetime) < '%s'
    #                                                 AND pt.id = ph.product_template_id
    #                                          ORDER  BY ph.datetime DESC
    #                                          LIMIT  1), 0)          AS cost_val,
    #                                0                                AS product_qty_out
    #                         FROM   stock_move sm
    #                                LEFT JOIN product_product pp
    #                                       ON sm.product_id = pp.id
    #                                LEFT JOIN product_template pt
    #                                       ON pp.product_tmpl_id = pt.id
    #                                LEFT JOIN stock_location sl
    #                                       ON sm.location_id = sl.id
    #                                LEFT JOIN product_category pc
    #                                       ON pt.categ_id = pc.id
    #                                LEFT JOIN product_uom pu
		# 		                          ON( pu.id = pt.uom_id )
    #                         WHERE  Date_trunc('day', sm.date) < '%s'
    #                                AND sm.state = 'done'
    #                                AND sm.location_id <> %s
    #                                AND sm.location_dest_id = %s
    #                                AND sm.picking_id IS NULL
    #                                AND pc.id IN %s
    #                         GROUP  BY sm.product_id,
    #                                   pt.name,
    #                                   pp.default_code,
    #                                   pt.id,
    #                                   pc.name,
    #                                   pu.name) table_dk
    #                 GROUP  BY product_id,
    #                           name,
    #                           code,
    #                           cost_val,
    #                           uom_name,
    #                           category
    #           ''' % (date_start, date_start, location_outsource, location_outsource, category_param,
    #                  date_start, date_start, location_outsource, location_outsource, category_param,
    #                  date_start, date_start, location_outsource, location_outsource, category_param)
    #
    #     sql_in_tk = '''
    #                 SELECT product_id,
    #                        NAME,
    #                        code,
    #                        uom_name,
    #                        category,
    #                        cost_val AS rate_in,
    #                        Sum(qty_in_tk) AS qty_in_tk,
    #                        Sum(val_in_tk) AS val_in_tk
    #                 FROM   (SELECT sm.product_id,
    #                                pt.NAME,
    #                                pp.default_code                          AS code,
    #                                pu.name                                  AS uom_name,
    #                                pc.name                                  AS category,
    #                                sm.product_qty                           AS qty_in_tk,
    #                                sm.product_qty * COALESCE(price_unit, 0) AS val_in_tk,
    #                                COALESCE(price_unit, 0) AS cost_val
    #                         FROM   stock_picking sp
    #                                LEFT JOIN stock_move sm
    #                                       ON sm.picking_id = sp.id
    #                                LEFT JOIN product_product pp
    #                                       ON sm.product_id = pp.id
    #                                LEFT JOIN product_template pt
    #                                       ON pp.product_tmpl_id = pt.id
    #                                LEFT JOIN stock_location sl
    #                                       ON sm.location_id = sl.id
    #                                LEFT JOIN product_category pc
    #                                       ON pt.categ_id = pc.id
    #                                LEFT JOIN product_uom pu
		# 		                          ON( pu.id = pt.uom_id )
    #                         WHERE  Date_trunc('day', sm.date) BETWEEN '%s' AND '%s'
    #                                AND sm.state = 'done'
    #                                --AND sp.location_type = 'outsource_out'
    #                                AND sm.location_id <> %s
    #                                AND sm.location_dest_id = %s
    #                                AND pc.id IN %s
    #                        --AND usage like 'internal'
    #                        )t1
    #                 GROUP  BY product_id,
    #                           NAME,
    #                           code,
    #                           uom_name,
    #                           category,
    #                           cost_val
    #             ''' % (date_start, date_end, location_outsource, location_outsource, category_param)
    #
    #     sql_out_tk = '''
    #                 SELECT product_id,
    #                        name,
    #                        code,
    #                        uom_name,
    #                        category,
    #                        list_price AS rate_out,
    #                        Sum(qty_out_tk)              AS qty_out_tk,
    #                        Sum(qty_out_tk) * list_price AS val_out_tk
    #                 FROM   (SELECT sm.product_id,
    #                                pt.name,
    #                                pp.default_code         AS code,
    #                                pu.name                 AS uom_name,
    #                                pc.name                 AS category,
    #                                sm.product_qty          AS qty_out_tk,
    #                                pt.list_price,
    #                                Coalesce((SELECT ph.cost
    #                                          FROM   product_price_history ph
    #                                          WHERE  Date_trunc('day', ph.datetime) <= '%s'
    #                                                 AND pt.id = ph.product_template_id
    #                                          ORDER  BY ph.datetime DESC
    #                                          LIMIT  1), 0) AS val_out_tk
    #                         FROM   stock_picking sp
    #                                LEFT JOIN stock_move sm
    #                                       ON sm.picking_id = sp.id
    #                                LEFT JOIN product_product pp
    #                                       ON sm.product_id = pp.id
    #                                LEFT JOIN product_template pt
    #                                       ON pp.product_tmpl_id = pt.id
    #                                LEFT JOIN stock_location sl
    #                                       ON sm.location_id = sl.id
    #                                LEFT JOIN product_category pc
    #                                       ON pt.categ_id = pc.id
    #                                LEFT JOIN product_uom pu
		# 		                          ON( pu.id = pt.uom_id )
    #                         WHERE  Date_trunc('day', sm.date) BETWEEN '%s' AND '%s'
    #                                AND sm.state = 'done'
    #                                --AND sp.location_type = 'outsource_out'
    #                                AND sm.location_id = %s
    #                                AND sm.location_dest_id <> %s
    #                                AND pc.id IN %s
    #                        --AND usage like 'internal'
    #                        )t1
    #                 GROUP  BY product_id,
    #                           name,
    #                           code,
    #                           uom_name,
    #                           category,
    #                           list_price,
    #                           val_out_tk
    #             ''' % (date_end, date_start, date_end, location_outsource, location_outsource, category_param)
    #
    #     sql_ck = '''
    #                 SELECT product_id,
    #        name,
    #        code,
    #        uom_name,
    #        category,
    #        cost_val AS rate_ck,
    #        Sum(product_qty_in - product_qty_out)                AS qty_ck,
    #        ( cost_val * Sum(product_qty_in - product_qty_out) ) AS val_ck
    # FROM   (SELECT sm.product_id,
    #                pt.name,
    #                pp.default_code                  AS code,
    #                pu.name                          AS uom_name,
    #                pc.name                          AS category,
    #                Coalesce(Sum(sm.product_qty), 0) AS product_qty_in,
    #                Coalesce((SELECT ph.cost
    #                          FROM   product_price_history ph
    #                          WHERE  Date_trunc('day', ph.datetime) <= '%s'
    #                                 AND pt.id = ph.product_template_id
    #                          ORDER  BY ph.datetime DESC
    #                          LIMIT  1), 0)          AS cost_val,
    #                0                                AS product_qty_out
    #         FROM   stock_picking sp
    #                LEFT JOIN stock_move sm
    #                       ON sm.picking_id = sp.id
    #                LEFT JOIN product_product pp
    #                       ON sm.product_id = pp.id
    #                LEFT JOIN product_template pt
    #                       ON pp.product_tmpl_id = pt.id
    #                LEFT JOIN stock_location sl
    #                       ON sm.location_id = sl.id
    #                LEFT JOIN product_category pc
    #                       ON pt.categ_id = pc.id
    #                LEFT JOIN product_uom pu
    #                       ON( pu.id = pt.uom_id )
    #         WHERE  Date_trunc('day', sm.date) <= '%s'
    #                AND sm.state = 'done'
    #                --AND sp.location_type = 'outsource_out'
    #                AND sm.location_id <> %s
    #                AND sm.location_dest_id = %s
    #                AND pc.id IN %s
    #         --AND usage like 'internal'
    #         GROUP  BY sm.product_id,
    #                   pt.name,
    #                   pp.default_code,
    #                   pt.id,
    #                   pc.name,
    #                   pu.name
    #         UNION ALL
    #         SELECT sm.product_id,
    #                pt.name,
    #                pp.default_code                  AS code,
    #                pu.name                          AS uom_name,
    #                pc.name                          AS category,
    #                0                                AS product_qty_in,
    #                Coalesce((SELECT ph.cost
    #                          FROM   product_price_history ph
    #                          WHERE  Date_trunc('day', ph.datetime) <= '%s'
    #                                 AND pt.id = ph.product_template_id
    #                          ORDER  BY ph.datetime DESC
    #                          LIMIT  1), 0)          AS cost_val,
    #                Coalesce(Sum(sm.product_qty), 0) AS product_qty_out
    #         FROM   stock_picking sp
    #                LEFT JOIN stock_move sm
    #                       ON sm.picking_id = sp.id
    #                LEFT JOIN product_product pp
    #                       ON sm.product_id = pp.id
    #                LEFT JOIN product_template pt
    #                       ON pp.product_tmpl_id = pt.id
    #                LEFT JOIN stock_location sl
    #                       ON sm.location_id = sl.id
    #                LEFT JOIN product_category pc
    #                       ON pt.categ_id = pc.id
    #                LEFT JOIN product_uom pu
    #                       ON( pu.id = pt.uom_id )
    #         WHERE  Date_trunc('day', sm.date) <= '%s'
    #                AND sm.state = 'done'
    #                --AND sp.location_type = 'outsource_in'
    #                AND sm.location_id = %s
    #                AND sm.location_dest_id <> %s
    #                AND pc.id IN %s
    #         --AND usage like 'internal'
    #         GROUP  BY sm.product_id,
    #                   pt.name,
    #                   pp.default_code,
    #                   pt.id,
    #                   pc.name,
    #                   pu.name
    #         UNION ALL
    #         SELECT sm.product_id,
    #                pt.name,
    #                pp.default_code                  AS code,
    #                pu.name                          AS uom_name,
    #                pc.name                          AS category,
    #                Coalesce(Sum(sm.product_qty), 0) AS product_qty_in,
    #                Coalesce((SELECT ph.cost
    #                          FROM   product_price_history ph
    #                          WHERE  Date_trunc('day', ph.datetime) <= '%s'
    #                                 AND pt.id = ph.product_template_id
    #                          ORDER  BY ph.datetime DESC
    #                          LIMIT  1), 0)          AS cost_val,
    #                0                                AS product_qty_out
    #         FROM   stock_move sm
    #                LEFT JOIN product_product pp
    #                       ON sm.product_id = pp.id
    #                LEFT JOIN product_template pt
    #                       ON pp.product_tmpl_id = pt.id
    #                LEFT JOIN stock_location sl
    #                       ON sm.location_id = sl.id
    #                LEFT JOIN product_category pc
    #                       ON pt.categ_id = pc.id
    #                LEFT JOIN product_uom pu
    #                       ON( pu.id = pt.uom_id )
    #         WHERE  Date_trunc('day', sm.date) <= '%s'
    #                AND sm.state = 'done'
    #                AND sm.location_id <> %s
    #                AND sm.location_dest_id = %s
    #                AND pc.id IN %s
    #                AND sm.picking_id IS NULL
    #         GROUP  BY sm.product_id,
    #                   pt.name,
    #                   pp.default_code,
    #                   pt.id,
    #                   pc.name,
    #                   pu.name
    #         UNION ALL
    #         SELECT sm.product_id,
    #                pt.name,
    #                pp.default_code                  AS code,
    #                pu.name                          AS uom_name,
    #                pc.name                          AS category,
    #                0                                AS product_qty_in,
    #                Coalesce((SELECT ph.cost
    #                          FROM   product_price_history ph
    #                          WHERE  Date_trunc('day', ph.datetime) <= '%s'
    #                                 AND pt.id = ph.product_template_id
    #                          ORDER  BY ph.datetime DESC
    #                          LIMIT  1), 0)          AS cost_val,
    #                Coalesce(Sum(sm.product_qty), 0) AS product_qty_out
    #         FROM   stock_move sm
    #                LEFT JOIN product_product pp
    #                       ON sm.product_id = pp.id
    #                LEFT JOIN product_template pt
    #                       ON pp.product_tmpl_id = pt.id
    #                LEFT JOIN stock_location sl
    #                       ON sm.location_id = sl.id
    #                LEFT JOIN product_category pc
    #                       ON pt.categ_id = pc.id
    #                LEFT JOIN product_uom pu
    #                       ON( pu.id = pt.uom_id )
    #         WHERE  Date_trunc('day', sm.date) <= '%s'
    #                AND sm.state = 'done'
    #                AND sm.location_id = %s
    #                AND sm.location_dest_id <> %s
    #                AND pc.id IN %s
    #                AND sm.picking_id IS NULL
    #         GROUP  BY sm.product_id,
    #                   pt.name,
    #                   pp.default_code,
    #                   pt.id,
    #                   pc.name,
    #                   pu.name) table_ck
    # GROUP  BY product_id,
    #           name,
    #           code,
    #           uom_name,
    #           category,
    #           cost_val
    #             ''' % (date_end, date_end, location_outsource, location_outsource, category_param,
    #                    date_end, date_end, location_outsource, location_outsource, category_param,
    #                    date_end, date_end, location_outsource, location_outsource, category_param,
    #                    date_end, date_end, location_outsource, location_outsource, category_param)
    #
    #     sql = '''
    #                 SELECT ROW_NUMBER() OVER(ORDER BY table_ck.code DESC) AS id ,
    #                         table_ck.product_id, table_ck.name, table_ck.uom_name, table_ck.code,
    #                         table_ck.category,
    #                         COALESCE(table_dk.rate_dk,0) as rate_dk,
    #                         COALESCE(table_in_tk.rate_in,0) as rate_in,
    #                         COALESCE(table_out_tk.rate_out,0) as rate_out,
    #                         COALESCE(table_ck.rate_ck,0) as rate_ck,
    #                         COALESCE(sum(qty_dk),0) as qty_dk,
    #                         COALESCE(sum(qty_in_tk),0) as qty_in_tk,
    #                         COALESCE(sum(qty_out_tk),0) as qty_out_tk,
    #                         COALESCE(sum(qty_ck),0)  as qty_ck,
    #                         COALESCE(sum(val_dk),0) as val_dk,
    #                         COALESCE(sum(val_in_tk),0) as val_in_tk,
    #                         COALESCE(sum(val_out_tk),0) as val_out_tk,
    #                         COALESCE(sum(val_ck),0)  as val_ck
    #                 FROM  (%s) table_ck
    #                     LEFT JOIN (%s) table_in_tk on table_ck.product_id = table_in_tk.product_id
    #                     LEFT JOIN (%s) table_out_tk on table_ck.product_id = table_out_tk.product_id
    #                     LEFT JOIN (%s) table_dk on table_ck.product_id = table_dk.product_id
    #                     GROUP BY table_ck.product_id, table_ck.name, table_ck.code,table_ck.category,
    #                     table_ck.uom_name,table_dk.rate_dk,table_in_tk.rate_in,table_out_tk.rate_out,table_ck.rate_ck
    #
    #             ''' % (sql_ck, sql_in_tk, sql_out_tk, sql_dk)
    #
    #     self.env.cr.execute(sql)
    #     for vals in self.env.cr.dictfetchall():
    #         if vals:
    #             category[vals['category']]['product'].append(vals)
    #
    #             total = category[vals['category']]['sub-total']
    #             total['total_dk_qty'] = total['total_dk_qty'] + vals['qty_dk']
    #             total['total_dk_val'] = total['total_dk_val'] + vals['val_dk']
    #             total['total_in_qty'] = total['total_in_qty'] + vals['qty_in_tk']
    #             total['total_in_val'] = total['total_in_val'] + vals['val_in_tk']
    #             total['total_out_qty'] = total['total_out_qty'] + vals['qty_out_tk']
    #             total['total_out_val'] = total['total_out_val'] + vals['val_out_tk']
    #             total['total_ck_qty'] = total['total_ck_qty'] + vals['qty_ck']
    #             total['total_ck_val'] = total['total_ck_val'] + vals['val_ck']
		#
		#
		# grand_total['total_dk_qty'] = grand_total['total_dk_qty'] + vals['qty_dk']
    #             grand_total['total_dk_val'] = grand_total['total_dk_val'] + vals['val_dk']
    #             grand_total['total_in_qty'] = grand_total['total_in_qty'] + vals['qty_in_tk']
    #             grand_total['total_in_val'] = grand_total['total_in_val'] + vals['val_in_tk']
    #             grand_total['total_out_qty'] = grand_total['total_out_qty'] + vals['qty_out_tk']
    #             grand_total['total_out_val'] = grand_total['total_out_val'] + vals['val_out_tk']
    #             grand_total['total_ck_qty'] = grand_total['total_ck_qty'] + vals['qty_ck']
    #             grand_total['total_ck_val'] = grand_total['total_ck_val'] + vals['val_ck']
    #
    #     return {'category': category, 'total': grand_total}
