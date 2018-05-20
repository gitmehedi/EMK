from odoo import api, fields, models, _

class StockTransferSummaryReport(models.AbstractModel):
    _name = 'report.stock_transfer_report.sts_report_temp'

    @api.multi
    def render_html(self, docids, data=None):
        get_data = self.get_report_data(data)
        docargs = {
            'doc_ids': self._ids,
            'docs': self,
            'record': data,
            'lines': get_data['dest_location'],
            'total': get_data['total'],
            'address': data['str_address'],
        }

        return self.env['report'].render('stock_transfer_report.sts_report_temp', docargs)

    def get_report_data(self, data):
        date_start = data['date_from']
        date_end = data['date_to']
        location_outsource = data['location_id']

        grand_total = {
            'title': 'GRAND TOTAL',
            'total_out_val': 0,
        }

        sql_out_tk = '''SELECT category,cetegory_id,
                               dest_location AS destination,
                               COALESCE(sum(sale_price * qty_out_tk),0) AS val_out_tk
                        FROM   (SELECT pp.id AS product_id,                               
                                    pc.name AS category,     
                                    sl1.name AS dest_location,
                                    sum(sm.product_qty) AS qty_out_tk,
                                    pt.list_price AS sale_price,
                                    pc.id AS cetegory_id
                                           
                                FROM   stock_move sm
                                       LEFT JOIN stock_picking sp
                                              ON sm.picking_id = sp.id
                                       LEFT JOIN product_product pp
                                              ON sm.product_id = pp.id
                                       LEFT JOIN product_template pt
                                              ON pp.product_tmpl_id = pt.id
                                       LEFT JOIN stock_location sl
                                              ON sm.location_id = sl.id
                                       LEFT JOIN stock_location sl1
                                              ON sm.location_dest_id = sl1.id
                                       LEFT JOIN product_category pc
                                              ON pt.categ_id = pc.id
                                           
                                WHERE  Date_trunc('day', sm.date) BETWEEN '%s' AND '%s'
                                       AND sm.state = 'done'
                                       AND sm.location_id = %s
                                       AND sm.location_dest_id <> %s
                                       group by pp.id,category,dest_location,pt.list_price,pc.id
                                   )tbl
                                GROUP  BY category,destination,cetegory_id
                                ''' % ( date_start, date_end, location_outsource, location_outsource)

        self.env.cr.execute(sql_out_tk)

        data_list = self.env.cr.dictfetchall()

        dest_location = {vals['destination']: {
            'categories': [],
            'sub-total': {
                'title': 'Sub Total',
                'total_out_val': 0,
            }
        }for vals in data_list}

        for vals in data_list:
            if vals:
                dest_location[vals['destination']]['categories'].append(vals)

                total = dest_location[vals['destination']]['sub-total']
                # total['name'] = vals['destination']

                total['total_out_val'] = total['total_out_val'] + vals['val_out_tk']
                grand_total['total_out_val'] = grand_total['total_out_val'] + vals['val_out_tk']

        return {'dest_location': dest_location, 'total': grand_total}


       # sql = ''' SELECT ROW_NUMBER() OVER(ORDER BY table_ck.cetegory_id DESC) AS id ,
        #                                     table_ck.category,
        #                                     table_ck.destination,
        #                                     COALESCE(table_ck.val_out_tk,0) AS val_out_tk
        #                             FROM  (%s) table_ck
        #                         ''' % (sql_out_tk)
