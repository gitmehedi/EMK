from odoo import api, fields, models, _
from odoo.tools.misc import formatLang


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
            'product_lines': get_data['category'],
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
        category_id = data['category_id']
        cat_pool = self.env['product.category']

        if category_id:
            categories = cat_pool.get_categories(category_id)
            category = {val.name: {
                'product': [],
                'sub-total': {
                    'title': 'SUB TOTAL',
                    'sub_total_qty': 0.0,
                    'sub_total_val': 0.0,
                }
            } for val in cat_pool.search([('id', 'in', categories)])}

            category_param = "(" + str(data['category_id']) + ")"
        else:
            cat_lists = cat_pool.search([], order='name ASC')
            category = {val.name: {
                'product': [],
                'sub-total': {
                    'title': 'SUB TOTAL',
                    'sub_total_qty': 0.0,
                    'sub_total_val': 0.0,
                }
            } for val in cat_lists}

            category_param = str(tuple(cat_lists.ids))

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
                                           AND pc.id IN %s
                                    ORDER  BY
                                           sm.date
                                   )tbl
                                    ''' % (date_start, date_end, location_outsource, location_outsource,category_param)

        self.env.cr.execute(sql_out_tk)
        for vals in self.env.cr.dictfetchall():
            if vals:
                category[vals['category']]['product'].append(vals)
                total = category[vals['category']]['sub-total']

                if total['sub_total_val']:
                    sub_total_val = float(total['sub_total_val'].replace(',',''))
                else:
                    sub_total_val = 0.0

                total['sub_total_qty'] = total['sub_total_qty'] + vals['qty_out_tk']
                sub_total_val = sub_total_val + vals['val_out_tk']

                total['sub_total_val'] = formatLang(self.env, float(sub_total_val))

                grand_total['total_out_qty'] = grand_total['total_out_qty'] + vals['qty_out_tk']
                grand_total['total_out_val'] = grand_total['total_out_val'] + vals['val_out_tk']

                vals['val_out_tk'] = formatLang(self.env, vals['val_out_tk'])

        grand_total['total_out_val'] = formatLang(self.env, grand_total['total_out_val'])
        return {'category': category, 'total': grand_total}