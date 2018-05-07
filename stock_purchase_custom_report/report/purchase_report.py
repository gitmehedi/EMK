from odoo import api, models

class StockPurchaseReport(models.AbstractModel):
    _name = 'report.stock_purchase_custom_report.purchase_report_template'

    @api.multi
    def render_html(self, docids, data=None):

        get_data = self.get_report_data(data)

        docargs = {
            'doc_ids': self._ids,
            'docs': self,
            'record': data,
            'lines': get_data['sub_list'],
            'total': get_data['total'],

        }
        return self.env['report'].render('stock_purchase_custom_report.purchase_report_template', docargs)

    def get_report_data(self, data):
        date_start = data['date_from']
        date_end = data['date_to']
        location_outsource = data['operating_unit_id']
        supplier_id = data['partner_id']

        sub_list = {
            'product': [],
            'sub-total': {
                'title': 'Sub Total',
                'total_in_qty': 0,
                'total_in_val': 0,
            }
        }


        grand_total = {
            'title': 'GRAND TOTAL',
            'total_in_qty': 0,
            'total_in_val': 0,
        }

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
                                           sm.product_qty * COALESCE(price_unit, 0) AS val_in_tk,
                                           COALESCE(price_unit, 0) AS cost_val
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
                                   --AND usage like 'internal' 
                                   )t1 
                            GROUP  BY product_id, 
                                      NAME, 
                                      code,
                                      uom_name,
                                      category,
                                      cost_val 
                        ''' % (date_start, date_end, location_outsource, location_outsource)

        sql = '''SELECT ROW_NUMBER() OVER(ORDER BY table_ck.code DESC) AS id ,
                                    table_ck.product_id, 
                                    table_ck.name, 
                                    table_ck.uom_name, 
                                    table_ck.code,
                                    table_ck.category, 
                                    COALESCE(table_ck.rate_in,0) as rate_in,
                                    COALESCE(sum(qty_in_tk),0) as qty_in_tk ,
                                    COALESCE(sum(val_in_tk),0) as val_in_tk
                            FROM  (%s) table_ck
                                GROUP BY table_ck.product_id, table_ck.name, table_ck.code,table_ck.category,table_ck.uom_name,table_ck.rate_in

                        ''' % (sql_in_tk)

        self.env.cr.execute(sql)
        for vals in self.env.cr.dictfetchall():
            if vals:
                sub_list['product'].append(vals)

                total = sub_list['sub-total']
                total['name'] = vals['name']

                total['total_in_qty'] = total['total_in_qty'] + vals['qty_in_tk']
                total['total_in_val'] = total['total_in_val'] + vals['val_in_tk']

                grand_total['total_in_qty'] = grand_total['total_in_qty'] + vals['qty_in_tk']
                grand_total['total_in_val'] = grand_total['total_in_val'] + vals['val_in_tk']


        return {'sub_list': sub_list, 'total': grand_total}
