from odoo import api, fields, models, _


class StockTransferDetailsReport(models.AbstractModel):
    _name = 'report.stock_transfer_report.std_report_temp'

    @api.multi
    def render_html(self, docids, data=None):

        get_data = self.get_report_data(data)
        report_utility_pool = self.env['report.utility']
        op_unit_id = data['operating_unit_id']
        op_unit_obj = self.env['operating.unit'].search([('id', '=', op_unit_id)])
        data['address'] = report_utility_pool.getAddressByUnit(op_unit_obj)

        docargs = {
            'doc_ids': self._ids,
            'docs': self,
            'record': data,
            'product_lines': get_data['product'],
            'total': get_data['total'],
            'address': data['address'],

        }
        return self.env['report'].render('stock_transfer_report.std_report_temp', docargs)

    def get_report_data(self, data):
        date_from = data['date_from']
        date_start = date_from + ' 00:00:00'
        date_to = data['date_to']
        date_end = date_to + ' 23:59:59'
        location_outsource = data['location_id']
        product = []
        grand_total = {
            'title': 'GRAND TOTAL',
            'total_out_qty': 0,
            'total_out_val': 0,
        }
        sql_out_tk = '''SELECT product_id,
                               name,
                               code,
                               uom_name,
                               category,
                               move_date AS m_date,
                               move_origin AS reference,
                               cost_val AS rate_out,
                               COALESCE(qty_out_tk,0)             AS qty_out_tk,
                               val_out_tk AS val_out_tk
                               FROM (SELECT sm.product_id,
                                           pt.name,
                                           pp.default_code         AS code,
                                           pu.name                 AS uom_name,
                                           pc.name                 AS category,
                                           sm.date + interval'6h'  AS move_date,
                                           sm.origin               AS move_origin,
                                           sm.product_qty          AS qty_out_tk,
                                           Coalesce((SELECT ph.current_price
                                             FROM   product_cost_price_history ph
                                             WHERE  to_char(ph.modified_datetime, 'YYYY-MM-DD HH24:MI') <= to_char(sm.date, 'YYYY-MM-DD HH24:MI')
                                                    AND pp.id = ph.product_id
                                             ORDER  BY ph.modified_datetime DESC,ph.id DESC
                                             LIMIT  1), 0) AS cost_val,
                                           sm.product_qty * Coalesce((SELECT ph.current_price
                                             FROM   product_cost_price_history ph
                                             WHERE  to_char(ph.modified_datetime, 'YYYY-MM-DD HH24:MI') <= to_char(sm.date, 'YYYY-MM-DD HH24:MI')
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
                                    ORDER  BY
                                           sm.date
                                   )tbl
                                    ''' % (date_start, date_end, location_outsource, location_outsource)

        self.env.cr.execute(sql_out_tk)
        for vals in self.env.cr.dictfetchall():
            if vals:
                product.append(vals)
                grand_total['total_out_qty'] = grand_total['total_out_qty'] + vals['qty_out_tk']
                grand_total['total_out_val'] = grand_total['total_out_val'] + vals['val_out_tk']

        return {'product': product, 'total': grand_total}