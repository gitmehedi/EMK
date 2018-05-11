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
            'lines': get_data['supplier'],
            'total': get_data['total'],
            'address': data['str_address'],

        }
        return self.env['report'].render('stock_purchase_custom_report.purchase_report_template', docargs)

    def get_report_data(self, data):
        date_start = data['date_from']
        date_end = data['date_to']
        # op_unit_id = data['operating_unit_id']
        location_outsource = data['location_id']
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

        if supplier_id:
            supplier_param = "(" + str(data['partner_id']) + ")"
        else:
            supplier_param = str(tuple(supplier_lists.ids))


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
                                           sm.date                                  AS move_date,
                                           sm.product_qty                           AS qty_in_tk, 
                                           sm.product_qty * COALESCE(price_unit, 0) AS val_in_tk,
                                           COALESCE(price_unit, 0) AS cost_val
                                    FROM   stock_picking sp 
                                           INNER JOIN stock_picking sp1 
                                                  ON sp.origin = sp1.name
                                           LEFT JOIN res_partner rp
						                          ON rp.id = sp1.partner_id
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
                                           AND sm.location_id <> %s
                                           AND sm.location_dest_id = %s
                                           AND sp1.partner_id IN %s
                                   )tbl 
                                   ORDER BY m_date
                        ''' % (date_start, date_end, location_outsource, location_outsource,supplier_param)

        self.env.cr.execute(sql_in_tk)
        for vals in self.env.cr.dictfetchall():
            if vals:
                supplier[vals['supplier']]['product'].append(vals)

                total = supplier[vals['supplier']]['sub-total']
                total['name'] = vals['supplier']

                total['total_in_qty'] = total['total_in_qty'] + vals['qty_in_tk']
                total['total_in_val'] = total['total_in_val'] + vals['val_in_tk']

                grand_total['total_in_qty'] = grand_total['total_in_qty'] + vals['qty_in_tk']
                grand_total['total_in_val'] = grand_total['total_in_val'] + vals['val_in_tk']


        return {'supplier': supplier, 'total': grand_total}


        # sql = '''SELECT ROW_NUMBER() OVER(ORDER BY table_ck.code DESC) AS id ,
        #                             table_ck.product_id,
        #                             table_ck.name,
        #                             table_ck.uom_name,
        #                             table_ck.code,
        #                             table_ck.category,
        #                             table_ck.supplier,
        #                             table_ck.m_date,
        #                             table_ck.mrr,
        #                             COALESCE(table_ck.rate_in,0) as rate_in,
        #                             COALESCE(table_ck.qty_in_tk,0) as qty_in_tk ,
        #                             COALESCE(table_ck.val_in_tk,0) as val_in_tk
        #                     FROM  (%s) table_ck
        #
        #                 ''' % (sql_in_tk)
