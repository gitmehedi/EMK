from openerp import api, models


class ProductCategorySummaryReport(models.AbstractModel):
    _name = 'report.category_stock_summary_reports.report_product_category_summary_qweb'

    sql_str = """SELECT pp.default_code,
                       pp.name_template,
                       pb.name,
                       (SELECT STRING_AGG(Name, ', ') FROM product_attribute_value_product_product_rel pavpp
                        LEFT JOIN product_attribute_value pav
                         ON (pav.id=pavpp.att_id)
                        WHERE pp.id = pavpp.prod_id
                        ) AS attribute,
                       pt.categ_id,
                       pt.list_price AS sale_price,
                       COALESCE((SELECT ph.cost 
                                 FROM   product_price_history ph 
                                 WHERE  pt.id = ph.product_template_id 
                                 ORDER  BY ph.datetime DESC 
                                 LIMIT  1), 0)          AS cost_price, 
                       COALESCE(SUM(stock.rec_qty),0) AS rec_qty,
                       COALESCE(SUM(stock.sale_qty),0) AS sale_qty,
                       COALESCE(SUM(stock.rec_qty) - (SUM(stock.sale_qty) + SUM(stock.move_qty)),0) AS stock_qty,
                       COALESCE(SUM(stock.move_qty),0) AS move_qty
                FROM product_template pt
                LEFT JOIN product_product pp ON (pp.product_tmpl_id=pt.id)
                LEFT JOIN product_brand pb ON (pb.id = pt.product_brand_id)
                LEFT JOIN
                  (SELECT rec.product_id,
                          COALESCE(rec.rec_qty,0) AS rec_qty,
                          COALESCE(sale.sale_qty,0) AS sale_qty,
                          COALESCE(mv.move_qty,0) AS move_qty
                   FROM
                     (SELECT sm.product_id,
                             COALESCE(SUM(sm.product_qty),0) AS rec_qty
                      FROM stock_move sm
                      LEFT JOIN stock_location sl 
                          ON (sl.id = sm.location_id)
                      WHERE sm.location_dest_id = %s 
                            AND sm.location_id IN (SELECT id FROM stock_location WHERE usage !='customer') 
                      GROUP BY sm.product_id
                      ORDER BY product_id ASC) rec
                   LEFT JOIN
                     (SELECT sm.product_id,
                             COALESCE(SUM(sm.product_qty),0) AS sale_qty
                      FROM stock_move sm
                      LEFT JOIN stock_location sl 
                         ON (sl.id=sm.location_id)
                      WHERE sm.location_id=%s
                        AND sm.location_dest_id IN (SELECT id FROM stock_location WHERE usage='customer')
                      GROUP BY sm.product_id
                      ORDER BY sm.product_id ASC) sale 
                     ON (rec.product_id = sale.product_id)
                   LEFT JOIN
                     (SELECT sm.product_id,
                             COALESCE(SUM(sm.product_qty),0) AS move_qty
                      FROM stock_move sm
                      LEFT JOIN stock_location sl ON (sl.id=sm.location_id)
                      WHERE sm.location_id=%s
                        AND sm.location_dest_id IN (SELECT id FROM stock_location WHERE usage !='customer' AND id!=%s)
                      GROUP BY sm.product_id
                      ORDER BY sm.product_id ASC) mv 
                      ON (rec.product_id = mv.product_id)) stock 
                               ON (stock.product_id = pp.id)
                    WHERE pt.categ_id=%s
                    GROUP BY pp.default_code,
                             pp.name_template,
                             pt.categ_id,
                             pt.list_price,
                             pt.id,
                             pp.id,
                             pb.name
                    ORDER BY pp.default_code ASC
    """


    sql_all = """SELECT pp.default_code,
                           pp.name_template,
                           pb.name,
                           (SELECT STRING_AGG(Name, ', ') FROM product_attribute_value_product_product_rel pavpp
                            LEFT JOIN product_attribute_value pav
                             ON (pav.id=pavpp.att_id)
                            WHERE pp.id = pavpp.prod_id
                            ) AS attribute,
                           pt.categ_id,
                           pt.list_price AS sale_price,
                           COALESCE((SELECT ph.cost 
                                     FROM   product_price_history ph 
                                     WHERE  pt.id = ph.product_template_id 
                                     ORDER  BY ph.datetime DESC 
                                     LIMIT  1), 0)          AS cost_price, 
                           COALESCE(SUM(stock.rec_qty),0) AS rec_qty,
                           COALESCE(SUM(stock.sale_qty),0) AS sale_qty,
                           COALESCE(SUM(stock.rec_qty) - SUM(stock.sale_qty),0) AS stock_qty
                    FROM product_template pt
                    LEFT JOIN product_product pp ON (pp.product_tmpl_id=pt.id)
                    LEFT JOIN product_brand pb ON (pb.id = pt.product_brand_id)
                    LEFT JOIN
                      (SELECT rec.product_id,
                              COALESCE(rec.rec_qty,0) AS rec_qty,
                              COALESCE(sale.sale_qty,0) AS sale_qty
                       FROM
                         (SELECT sm.product_id,
                                 COALESCE(SUM(sm.product_qty),0) AS rec_qty
                          FROM stock_move sm
                          LEFT JOIN stock_location sl 
                              ON (sl.id = sm.location_id)
                          WHERE sm.location_id IN (SELECT id FROM stock_location WHERE usage ='supplier') 
                          GROUP BY sm.product_id
                          ORDER BY product_id ASC) rec
                       LEFT JOIN
                         (SELECT sm.product_id,
                                 COALESCE(SUM(sm.product_qty),0) AS sale_qty
                          FROM stock_move sm
                          LEFT JOIN stock_location sl 
                             ON (sl.id=sm.location_id)
                          WHERE sm.location_dest_id IN (SELECT id FROM stock_location WHERE usage='customer')
                          GROUP BY sm.product_id
                          ORDER BY sm.product_id ASC) sale 
                         ON (rec.product_id = sale.product_id)) stock 
                            ON (stock.product_id = pp.id)
                        WHERE pt.categ_id=%s
                        GROUP BY pp.default_code,
                                 pp.name_template,
                                 pt.categ_id,
                                 pt.list_price,
                                 pt.id,
                                 pp.id,
                                 pb.name
                        ORDER BY pp.default_code ASC
        """

    @api.multi
    def render_html(self, data=None):
        report_data = self.get_data(data)
        docargs = {
            'data': data,
            'report_data': report_data,
        }
        return self.env['report'].render('category_stock_summary_reports.report_product_category_summary_qweb', docargs)

    def get_data(self, data):
        report_data = []

        if data['location_id']:
            self._cr.execute(self.sql_str, (
                data['location_id'], data['location_id'], data['location_id'], data['location_id'],
                data['category_id']))
        else:
            self._cr.execute(self.sql_all, (data['category_id'],))

        for val in self._cr.fetchall():
            temp_dict = {}
            temp_dict['code'] = val[0]
            temp_dict['name'] = val[1]
            temp_dict['brand'] = val[2]
            temp_dict['attributes'] = val[3]
            temp_dict['sale_price'] = val[5]
            temp_dict['cost_price'] = val[6]
            temp_dict['received_qty'] = val[7]
            temp_dict['sale_qty'] = val[8]
            temp_dict['on_hand'] = val[9]
            if data['location_id']:
                temp_dict['move_qty'] = val[10]
            report_data.append(temp_dict)

        return report_data
