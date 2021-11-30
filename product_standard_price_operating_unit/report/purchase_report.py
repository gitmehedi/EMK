from odoo import api, models


class StockPurchaseReport(models.AbstractModel):
    _inherit = 'report.stock_purchase_custom_report.purchase_report_template'

    def get_report_data(self, data):
        date_from = data['date_from']
        date_start = date_from + ' 00:00:00'
        date_to = data['date_to']
        date_end = date_to + ' 23:59:59'
        location_outsource = data['location_id']
        supplier_id = data['partner_id']
        operating_unit_id = data['operating_unit_id']
        location_input = self.env['stock.location'].search([('operating_unit_id', '=', data['operating_unit_id']),
                                                            ('name', '=', 'Input')], limit=1).id

        _where = ''
        if supplier_id:
            _where = ' AND tbl.partner_id={0}'.format(data['partner_id'])

        sql_in_tk = '''SELECT 
                            sm.product_id, 
                            pt.name, 
                            pp.default_code AS code,
                            pu.name AS uom_name, 
                            pc.name AS category, 
                            tbl.partner_id AS partner_id,
                            rp.name AS partner_name,
                            sp.mrr_no AS mrr,
                            sm.date + interval'6h' AS m_date,
                            sm.product_qty AS qty_in_tk, 
                            sm.product_qty * Coalesce((SELECT ph.cost
                                FROM product_price_history ph
                                WHERE to_char(ph.datetime, 'YYYY-MM-DD HH24:MI') <= to_char(sm.date, 'YYYY-MM-DD HH24:MI') 
                                    AND pp.id = ph.product_id AND ph.operating_unit_id=%s
                                ORDER BY ph.datetime DESC,ph.id DESC
                                LIMIT 1), 0) AS val_in_tk,
                            Coalesce((SELECT ph.cost
                                FROM product_price_history ph
                                WHERE to_char(ph.datetime, 'YYYY-MM-DD HH24:MI') <= to_char(sm.date, 'YYYY-MM-DD HH24:MI')
                                    AND pp.id = ph.product_id AND ph.operating_unit_id=%s
                                ORDER BY ph.datetime DESC,ph.id DESC
                                LIMIT 1), 0) AS rate_in
                        FROM   
                            stock_move sm 
                            JOIN stock_picking sp ON sm.picking_id = sp.id
                            JOIN (SELECT 
                                        DISTINCT sp.id AS picking_id,
                                        sp1.partner_id AS partner_id
                                    FROM 
                                        stock_move sm 
                                        JOIN stock_picking sp ON sm.picking_id = sp.id 
                                        JOIN stock_picking sp1
                                              ON CASE 
                                            WHEN sp1.location_dest_id=%s AND sp.origin = sp1.name THEN 1
                                            WHEN sp1.location_dest_id=%s AND sp.origin = sp1.origin THEN 1
                                            ELSE 0																								
                                            END = 1
                                        JOIN stock_picking_type spt ON spt.id=sp.picking_type_id AND code='internal'               
                                    WHERE 
                                        sm.date + interval'6h' BETWEEN '%s' AND '%s' 
                                        AND sm.state = 'done' 
                                        AND sm.location_id <> %s
                                        AND sm.location_dest_id = %s) AS tbl ON tbl.picking_id=sm.picking_id
                            JOIN res_partner rp ON rp.id = tbl.partner_id
                            LEFT JOIN product_product pp ON sm.product_id = pp.id 
                            LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id 
                            LEFT JOIN stock_location sl ON sm.location_id = sl.id 
                            LEFT JOIN product_category pc ON pt.categ_id = pc.id
                            LEFT JOIN product_uom pu ON pu.id = pt.uom_id                                         
                        WHERE  
                            sm.date + interval'6h' BETWEEN '%s' AND '%s' 
                            AND sm.state = 'done' 
                            AND sm.location_id <> %s
                            AND sm.location_dest_id = %s
                            %s
                        ORDER BY
                            sm.date
        ''' % (operating_unit_id, operating_unit_id, location_input, location_input, date_start, date_end,
               location_outsource, location_outsource, date_start, date_end, location_outsource, location_outsource,
               _where)

        supplier_dict = dict()
        grand_total = {
            'title': 'GRAND TOTAL',
            'total_in_qty': 0,
            'total_in_val': 0,
        }

        self.env.cr.execute(sql_in_tk)
        for row in self.env.cr.dictfetchall():
            if row['partner_id'] not in supplier_dict:
                supplier_dict[row['partner_id']] = dict()
                supplier_dict[row['partner_id']]['partner_name'] = row['partner_name']
                supplier_dict[row['partner_id']]['product'] = list()
                supplier_dict[row['partner_id']]['product'].append(row)
            else:
                supplier_dict[row['partner_id']]['product'].append(row)

            # grand total calculation
            grand_total['total_in_qty'] = grand_total['total_in_qty'] + float(row['qty_in_tk'])
            grand_total['total_in_val'] = grand_total['total_in_val'] + float(row['val_in_tk'])

        return {'supplier': supplier_dict, 'total': grand_total}
