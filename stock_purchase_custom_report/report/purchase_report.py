from odoo import api, models
from odoo.tools.misc import formatLang

class StockPurchaseReport(models.AbstractModel):
    _name = 'report.stock_purchase_custom_report.purchase_report_template'

    @api.multi
    def render_html(self, docids, data=None):

        get_data = self.get_report_data(data)
        report_utility_pool = self.env['report.utility']
        op_unit_id = data['operating_unit_id']
        op_unit_obj = self.env['operating.unit'].search([('id','=',op_unit_id)])
        data['address'] = report_utility_pool.getAddressByUnit(op_unit_obj)

        docargs = {
            'doc_ids': self._ids,
            'docs': self,
            'record': data,
            'lines': get_data['supplier'],
            'total': get_data['total'],
            'address': data['address'],

        }
        return self.env['report'].render('stock_purchase_custom_report.purchase_report_template', docargs)

    def get_report_data(self, data):
        date_from = data['date_from']
        date_start = date_from + ' 00:00:00'
        date_to = data['date_to']
        date_end = date_to + ' 23:59:59'
        location_outsource = data['location_id']
        location_input =  self.env['stock.location'].search(
            [('operating_unit_id', '=', data['operating_unit_id']),('name', '=', 'Input')],limit=1).id
        supplier_id = data['partner_id']
        supplier_pool = self.env['res.partner']
        picking_pool = self.env['stock.picking'].search([])
        pick_loc_list = []

        for picking_obj in picking_pool:
            location_id = picking_obj.partner_id.id
            pick_loc_list.append(location_id)

        if supplier_id:
            supplier ={ val.name:{
                'product': [],
                'sub-total': {
                    'title': 'Sub Total',
                    'total_in_qty': 0,
                    'total_in_val': 0,
                }
            } for val in supplier_pool.search([('id','=',supplier_id)])}
        else:
            supplier_lists = supplier_pool.search([('id','in',pick_loc_list)], order='name ASC')
            supplier = {val.name: {
                'product': [],
                'sub-total': {
                    'title': 'Sub Total',
                    'total_in_qty': 0,
                    'total_in_val': 0,
                }
            } for val in supplier_lists}

        _where = ''
        if supplier_id:
            _where = ' AND sp1.partner_id IN ({0})'.format(data['partner_id'])
        elif supplier_lists:
            if len(supplier_lists) == 1:
                _where = ' AND sp1.partner_id IN ({0})'.format(supplier_lists.id)
            else:
                _where = ' AND sp1.partner_id IN {0}'.format(tuple(supplier_lists.ids))

        grand_total = {
            'title': 'GRAND TOTAL',
            'total_in_qty': 0,
            'total_in_val': 0,
        }

        sql_in_tk = '''SELECT product_id, 
                                   NAME, 
                                   code,
                                   uom_name, 
                                   category,
                                   cost_val AS rate_in,
                                   partner_id,
                                   partner_name AS supplier,
                                   move_date AS m_date,
                                   sp_mrr AS mrr,
                                   qty_in_tk AS qty_in_tk, 
                                   val_in_tk AS val_in_tk 
                            FROM   (SELECT sm.product_id, 
                                           pt.NAME, 
                                           pp.default_code                          AS code,
                                           pu.name                                  AS uom_name, 
                                           pc.name                                  AS category, 
                                           sp1.partner_id			                AS partner_id,
                                           rp.name			                        AS partner_name,
                                           sp.mrr_no				                AS sp_mrr,
                                           sm.date + interval'6h'                   AS move_date,
                                           sm.product_qty                           AS qty_in_tk, 
                                           sm.product_qty * Coalesce((SELECT ph.current_price
                                             FROM   product_cost_price_history ph
                                             WHERE  to_char(ph.modified_datetime, 'YYYY-MM-DD HH24:MI') <= to_char(sm.date, 'YYYY-MM-DD HH24:MI') 
                                                    AND pp.id = ph.product_id
                                             ORDER  BY ph.modified_datetime DESC,ph.id DESC
                                             LIMIT  1), 0) AS val_in_tk,
                                           Coalesce((SELECT ph.current_price
                                             FROM   product_cost_price_history ph
                                             WHERE  to_char(ph.modified_datetime, 'YYYY-MM-DD HH24:MI') <= to_char(sm.date, 'YYYY-MM-DD HH24:MI')
                                                    AND pp.id = ph.product_id
                                             ORDER  BY ph.modified_datetime DESC,ph.id DESC
                                             LIMIT  1), 0)          AS cost_val
                                    FROM   stock_move sm 
                                           LEFT JOIN stock_picking sp 
                                                  ON sm.picking_id = sp.id 
                                           INNER JOIN stock_picking sp1 
                                                  ON CASE 
                                                WHEN sp1.location_dest_id = %s AND sp.origin = sp1.name THEN 1
                                                WHEN sp1.location_dest_id = %s AND sp.origin = sp1.origin THEN 1
                                                ELSE 0																								
                                                END = 1
                                           LEFT JOIN res_partner rp
						                          ON rp.id = sp1.partner_id
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
                                           AND sm.location_id <> %s
                                           AND sm.location_dest_id = %s
                                            %s
                                   )tbl 
                                   ORDER BY m_date
                        ''' % (location_input,location_input,date_start, date_end, location_outsource, location_outsource,_where)

        self.env.cr.execute(sql_in_tk)
        for vals in self.env.cr.dictfetchall():
            if vals:
                supplier[vals['supplier']]['product'].append(vals)

                total = supplier[vals['supplier']]['sub-total']
                total['name'] = vals['supplier']

                if total['total_in_val']:
                    total_in_val = float(total['total_in_val'].replace(',',''))
                else:
                    total_in_val = 0.0

                total['total_in_qty'] = total['total_in_qty'] + vals['qty_in_tk']
                total_in_val = total_in_val + vals['val_in_tk']

                total['total_in_val'] = formatLang(self.env, float(total_in_val))

                grand_total['total_in_qty'] = grand_total['total_in_qty'] + vals['qty_in_tk']
                grand_total['total_in_val'] = grand_total['total_in_val'] + vals['val_in_tk']

                vals['val_in_tk'] = formatLang(self.env, vals['val_in_tk'])

                vals['rate_in'] = formatLang(self.env, vals['rate_in'])

        grand_total['total_in_val'] = formatLang(self.env,grand_total['total_in_val'])
        return {'supplier': supplier, 'total': grand_total}
