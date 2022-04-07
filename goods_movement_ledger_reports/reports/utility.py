from odoo import fields, models, api


class ProductReportUtility(models.TransientModel):
    _name = 'product.ledger.report.utility'
    _description = 'Product Report Utility'

    def get_total_return_qty_move(self, move_id):
        sql = '''
            SELECT COALESCE(SUM(sm.product_qty), 0) AS returned_qty FROM stock_move AS sm 
            WHERE sm.state = 'done' 
            AND origin_returned_move_id  = %s
        ''' % (move_id)
        self.env.cr.execute(sql)
        returned_qty = 0.0
        for vals in self.env.cr.dictfetchall():
            returned_qty = float(vals['returned_qty'])
        return returned_qty

    def get_opening_closing_stock(self, start_date, end_date, location_id, product_param):
        sql = '''
                select COALESCE(opening_stock, 0) as opening_stock,
                       COALESCE(closing_stock, 0) as closing_stock  
                from
                    (SELECT
                        product_id,
                        ROUND(Sum(product_qty_in - product_qty_out),
                        4)AS opening_stock                     
                    FROM
                        (SELECT
                            sm.product_id,
                            sm.date,
                            Coalesce(Sum(sm.product_qty),
                            0) AS product_qty_in,
                            0 AS product_qty_out                             
                        FROM
                            stock_move sm                               
                        LEFT JOIN
                            stock_picking sp                                     
                                ON sm.picking_id = sp.id                             
                        LEFT JOIN
                            product_product pp                                     
                                ON sm.product_id = pp.id                             
                        LEFT JOIN
                            product_template pt                                     
                                ON pp.product_tmpl_id = pt.id                             
                        LEFT JOIN
                            stock_location sl                                    
                                ON sm.location_id = sl.id                                              
                        LEFT JOIN
                            product_uom pu                                    
                                ON(
                                    pu.id = pt.uom_id 
                                ) 
                        WHERE
                            sm.date + interval'6h' < '%s'                                    
                            AND sm.state = 'done'                                    
                            AND sm.location_id NOT IN %s                                    
                            AND sm.location_dest_id IN %s                                                                        
                            AND pp.id IN %s

                        GROUP  BY
                            sm.product_id,
                            sm.date                             
                        UNION
                        ALL  SELECT
                            sm.product_id,
                            sm.date,
                            0 AS product_qty_in,
                            Coalesce(Sum(sm.product_qty),
                            0) AS product_qty_out                             
                        FROM
                            stock_move sm                                    
                        LEFT JOIN
                            stock_picking sp                                           
                                ON sm.picking_id = sp.id                                    
                        LEFT JOIN
                            product_product pp                                           
                                ON sm.product_id = pp.id                                    
                        LEFT JOIN
                            product_template pt                                           
                                ON pp.product_tmpl_id = pt.id                                    
                        LEFT JOIN
                            stock_location sl                                           
                                ON sm.location_id = sl.id                                                                    
                        LEFT JOIN
                            product_uom pu                               
                                ON(
                                    pu.id = pt.uom_id 
                                )                             
                        WHERE
                            sm.date + interval'6h' < '%s'                                     
                            AND sm.state = 'done'                                    
                            AND sm.location_id IN %s                                   
                            AND sm.location_dest_id NOT IN %s                                                                 
                            AND pp.id IN %s                         
                        GROUP  BY
                            sm.product_id,
                            sm.date                                                                    
                    ) table_dk                     
                GROUP  BY
                    product_id) os 
                full join
                (
                    SELECT
                        product_id,
                        ROUND(Sum(product_qty_in - product_qty_out),
                        4)   AS closing_stock             
                    FROM
                        (SELECT
                            sm.product_id,
                            sm.date,
                            Coalesce(Sum(sm.product_qty),
                            0) AS product_qty_in,
                            0 AS product_qty_out                     
                        FROM
                            stock_move sm                            
                        LEFT JOIN
                            stock_picking sp                                   
                                ON sm.picking_id = sp.id                            
                        LEFT JOIN
                            product_product pp                                   
                                ON sm.product_id = pp.id                            
                        LEFT JOIN
                            product_template pt                                   
                                ON pp.product_tmpl_id = pt.id                            
                        LEFT JOIN
                            stock_location sl                                   
                                ON sm.location_id = sl.id                                          
                        LEFT JOIN
                            product_uom pu                                   
                                ON(
                                    pu.id = pt.uom_id 
                                )                     
                        WHERE
                            sm.date + interval'6h' <= '%s'                                       
                            AND sm.state = 'done'      
                            AND sm.location_id NOT IN %s                             
                            AND sm.location_dest_id IN %s                                                                      
                            AND pp.id IN %s                  
                        GROUP  BY
                            sm.product_id,
                            sm.date                     
                        UNION
                        ALL                     SELECT
                            sm.product_id,
                            sm.date,
                            0   AS product_qty_in,
                            Coalesce(Sum(sm.product_qty),
                            0) AS product_qty_out                     
                        FROM
                            stock_move sm                            
                        LEFT JOIN
                            stock_picking sp                                   
                                ON sm.picking_id = sp.id                            
                        LEFT JOIN
                            product_product pp                                   
                                ON sm.product_id = pp.id                            
                        LEFT JOIN
                            product_template pt                                   
                                ON pp.product_tmpl_id = pt.id                            
                        LEFT JOIN
                            stock_location sl                                   
                                ON sm.location_id = sl.id                                                   
                        LEFT JOIN
                            product_uom pu                                   
                                ON(
                                    pu.id = pt.uom_id 
                                )                     
                        WHERE
                            sm.date + interval'6h' <= '%s'                                    
                            AND sm.state = 'done'           
                            AND sm.location_id IN %s                          
                            AND sm.location_dest_id NOT IN %s                                                                       
                            AND pp.id IN %s                            
                        GROUP  BY
                            sm.product_id,
                            sm.date                     
                    ) table_ck              
                GROUP  BY
                    product_id  ) cs 
                    on os.product_id = cs.product_id

            ''' % (
            start_date, location_id, location_id, product_param, start_date, location_id, location_id, product_param,
            end_date, location_id, location_id, product_param, end_date, location_id, location_id, product_param)
        self.env.cr.execute(sql)
        datewise_opening_closing_stocklist = []

        for vals in self.env.cr.dictfetchall():
            item = {'start_date': start_date, 'opening_stock': vals['opening_stock'],
                    'closing_stock': vals['closing_stock']}
            datewise_opening_closing_stocklist.append(item)
        return datewise_opening_closing_stocklist

    def get_production_stock(self, start_date, end_date, operating_unit_id, product_id):

        production_sql = '''
                        SELECT 
                           t1.product_id,t1.product_name,
                           t1.product_uom,t1.name,t1.avg_cost,
                           COALESCE(COALESCE(t1.total_qty, 0) - COALESCE(t2.total_qty, 0), 0) as after_total_qty,
                           COALESCE(t1.total_qty, 0) as production_qty,
                           COALESCE(t2.total_qty, 0) as unbuild_qty 
                        FROM
                           (
                              SELECT sm.product_id,AVG(sm.price_unit) as avg_cost,
                              pt.name AS product_name,sm.product_uom,uom.name,
                              SUM(sm.quantity_done_store) AS total_qty 
                              FROM
                                 stock_move sm 
                                 JOIN mrp_production mp ON mp.id = sm.production_id
                                 LEFT JOIN product_uom uom ON uom.id = sm.product_uom 
                                 LEFT JOIN product_product pp ON pp.id = sm.product_id 
                                 LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id 
                              WHERE
                                 mp.product_id = %s 
                                 AND mp.state = 'done' 
                                 AND sm.date + interval'6h' BETWEEN DATE('%s') + TIME '00:00:01' AND DATE('%s') + TIME '23:59:59' 
                                 AND sm.state = 'done' 
                                 AND mp.operating_unit_id = %s
                              GROUP BY
                                 sm.product_id,
                                 mp.product_id,
                                 pt.name,
                                 sm.product_uom,
                                 uom.name 
                              ORDER BY
                                 sm.product_id 
                           )
                           t1 
                           FULL JOIN
                              (
                                 SELECT
                                    sm.product_id,
                                    pt.name AS product_name,
                                    sm.product_uom,
                                    uom.name,
                                    SUM(sm.quantity_done_store) AS total_qty 
                                 FROM
                                    stock_move sm 
                                    JOIN mrp_unbuild mu on sm.consume_unbuild_id = mu.id
                                    LEFT JOIN product_uom uom ON uom.id = sm.product_uom 
                                    LEFT JOIN product_product pp ON pp.id = sm.product_id 
                                    LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id 
                                 WHERE
                                    sm.state = 'done' 
                                    AND mu.state = 'done' 
                                  
                                    AND sm.date + interval'6h' BETWEEN DATE('%s') + TIME '00:00:01' AND DATE('%s') + TIME '23:59:59' 
                                    AND mu.product_id = %s 
                                    AND mu.operating_unit_id = %s
                                 GROUP BY
                                    sm.product_id,
                                    mu.product_id,
                                    pt.name,
                                    sm.product_uom,
                                    uom.name 
                                 ORDER BY
                                    sm.product_id 
                              )
                              t2 
                              ON (t1.product_id = t2.product_id);
                ''' % (
            product_id, start_date, end_date, operating_unit_id, start_date, end_date,
            product_id, operating_unit_id)

        self.env.cr.execute(production_sql)
        production_total_qty = 0
        for vals in self.env.cr.dictfetchall():
            production_total_qty = vals['after_total_qty']
        return production_total_qty

    def get_purchase_stock(self, start_date, end_date, operating_unit_id, product_param):
        location_id = self.env['stock.location'].search(
            [('operating_unit_id', '=', operating_unit_id), ('name', '=', 'Stock')],
            limit=1).id
        location_main_stock = self.env['stock.location'].browse(location_id)
        input_location_id = self.env['stock.location'].search(
            [('operating_unit_id', '=', operating_unit_id), ('name', '=', 'Input')],
            limit=1).id

        qc_location_id = self.env['stock.location'].search(
            [('operating_unit_id', '=', operating_unit_id), ('name', '=', 'Quality Control')],
            limit=1).id

        picking_type_id = self.env['stock.picking.type'].search(
            [('code', '=', 'internal'), ('operating_unit_id', '=', operating_unit_id),
             ('default_location_src_id', '=', location_id), ('default_location_dest_id', '=', location_id)], limit=1).id

        received_sql = '''
            SELECT COALESCE(sm.product_qty, 0) AS total_product_qty FROM stock_move sm 
                LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
                WHERE sp.picking_type_id = %s
                        AND sp.location_id = %s
                        AND sp.location_dest_id = %s
                        AND sp.transfer_type IS NULL
                        AND sp.receive_type IS NULL
                        AND sm.product_id IN (%s)
                        AND sm.date BETWEEN DATE('%s')+TIME '00:00:01' AND DATE('%s')+TIME '23:59:59'
                        AND sm.state = 'done'
        ''' % (
            picking_type_id, qc_location_id, location_id, product_param, start_date, end_date)
        self.env.cr.execute(received_sql)
        total_received_qty = 0.0
        for values in self.env.cr.dictfetchall():
            total_received_qty = total_received_qty + float(values['total_product_qty'])

        returned_sql = '''
                    SELECT sm.id,sp.origin FROM stock_move sm 
                        LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
                        WHERE sp.picking_type_id = %s
                                AND sp.location_id = %s
                                AND sp.location_dest_id = %s
                                AND sp.transfer_type IS NULL
                                AND sp.receive_type IS NULL
                                AND sm.product_id IN (%s)
                                AND sm.date BETWEEN DATE('%s')+TIME '00:00:01' AND DATE('%s')+TIME '23:59:59'
                                AND sm.state = 'done'
                ''' % (
            picking_type_id, qc_location_id, location_id, product_param, start_date, end_date)
        self.env.cr.execute(returned_sql)
        total_returned_qty = 0.0

        # remove return qty if found || loan type qty if found || transfer type qty if found

        sub_loan_move = 0.0
        sub_transfer_move = 0.0
        for values in self.env.cr.dictfetchall():
            returned_qty = self.get_total_return_qty_move(values['id'])
            total_returned_qty = total_returned_qty + returned_qty
            origin_val = values['origin'].encode('ascii')
            # checking for loan type in input move (lenders -> input move using origin)

            input_stock_move = self.env['stock.move'].search(
                [('origin', '=', origin_val), ('location_dest_id', '=', input_location_id)])
            if len(input_stock_move) == 1:
                move_sql = '''SELECT picking_id,product_qty FROM stock_move WHERE product_id IN %s AND id = %s LIMIT 1''' % (
                    product_param, input_stock_move.id)
            else:
                move_sql = '''SELECT picking_id,product_qty FROM stock_move WHERE product_id IN %s AND id IN %s LIMIT 1''' % (
                product_param, tuple(input_stock_move.ids))

            self.env.cr.execute(move_sql)
            for move_val in self.env.cr.dictfetchall():
                if move_val['picking_id']:
                    picking_obj = self.env['stock.picking'].browse(move_val['picking_id'])
                    if picking_obj.transfer_type == 'loan' and picking_obj.receive_type == 'loan':
                        # found loan type in input move
                        sub_loan_move = sub_loan_move + float(move_val['product_qty'])

                    if picking_obj.location_id.usage == 'transit' and picking_obj.location_id.can_operating_unit_transfer:
                        # found transfer type in input move
                        sub_transfer_move = sub_transfer_move + float(move_val['product_qty'])
        datewise_purchase_stocklist = []
        item = {'purchase_qty': total_received_qty - total_returned_qty - sub_loan_move - sub_transfer_move}
        datewise_purchase_stocklist.append(item)
        return datewise_purchase_stocklist

    def _get_delivery_returned(self, operating_unit_id, date_from, date_to, product_id):
        delivery_returned_list = []
        sql_str = """
        SELECT
            sp.origin AS delivery_challan_no,
            SUM(spo.qty_done) AS returned_qty
        FROM
            stock_pack_operation spo
            JOIN stock_picking sp ON sp.id=spo.picking_id
            JOIN stock_picking_type spt ON spt.id=sp.picking_type_id AND spt.code='outgoing_return'
            JOIN operating_unit ou ON ou.id=sp.operating_unit_id
            JOIN product_product pp ON pp.id=spo.product_id
            JOIN product_template pt ON pt.id=pp.product_tmpl_id
            JOIN stock_picking dc ON dc.name=sp.origin
            JOIN sale_order so ON so.name=dc.origin
            JOIN res_partner rp ON rp.id=so.partner_id
        WHERE 
            sp.operating_unit_id=%s 
            AND DATE(sp.date_done + interval '6h') BETWEEN DATE('%s')+time '00:00' 
            AND DATE('%s')+time '23:59:59' AND spo.product_id=%s AND sp.state!='cancel' GROUP BY sp.origin
        """ % (operating_unit_id, date_from, date_to, product_id)

        self.env.cr.execute(sql_str)
        for row in self.env.cr.dictfetchall():
            delivery_returned_list.append(row)

        return delivery_returned_list

    def _get_delivery_done(self, operating_unit_id, date_from, date_to, product_id):
        sql_str = """
            SELECT
                spo.product_id,
                pt.name AS product_name,
                so.partner_id,
                rp.name AS partner_name,
                sp.origin AS so_no,
                so.date_order AS so_date,
                sp.date_done AS delivery_date,
                sp.name AS delivery_challan_no,
                sp.vat_challan_id AS vat_challan_no,
                lc.name AS contract_no,
                pm.packaging_mode AS packing_mode,
                spo.qty_done AS delivered_qty,
                sol.price_unit,
                sol.currency_id,
                rc.name AS currency_name,
                (spo.qty_done * sol.price_unit) AS amount
            FROM
                stock_pack_operation spo
                JOIN stock_picking sp ON sp.id=spo.picking_id
                JOIN stock_picking_type spt ON spt.id=sp.picking_type_id AND spt.code='outgoing'
                JOIN operating_unit ou ON ou.id=sp.operating_unit_id
                JOIN product_product pp ON pp.id=spo.product_id
                JOIN product_template pt ON pt.id=pp.product_tmpl_id
                JOIN sale_order so ON so.name=sp.origin
                JOIN sale_order_line sol ON sol.order_id=so.id
                JOIN res_partner rp ON rp.id=so.partner_id
                JOIN res_currency rc ON rc.id=sol.currency_id
                LEFT JOIN letter_credit lc ON lc.id=so.lc_id
                LEFT JOIN product_packaging_mode pm ON pm.id=so.pack_type
            WHERE 
                    sp.operating_unit_id=%s
                    AND DATE(sp.date_done + interval '6h') BETWEEN DATE('%s')+time '00:00' AND DATE('%s')+time '23:59:59' AND spo.product_id=%s AND sp.state='done'
            GROUP BY
                sp.name,spo.product_id,pt.name,so.partner_id,rp.name,sp.origin,so.date_order,
                sp.date_done,sp.vat_challan_id,lc.name,pm.packaging_mode,spo.qty_done,sol.price_unit,sol.currency_id,rc.name
            ORDER BY 
                sp.date_done
        """ % (operating_unit_id, date_from, date_to, product_id)

        delivery_done_dict = {}
        delivery_returned_list = self._get_delivery_returned(operating_unit_id, date_from, date_to, product_id)

        self.env.cr.execute(sql_str)
        for row in self.env.cr.dictfetchall():
            returned_qty = sum(map(lambda d: d['returned_qty'],
                                   filter(lambda x: x['delivery_challan_no'] == row['delivery_challan_no'],
                                          delivery_returned_list)))
            row['delivered_qty'] = row['delivered_qty'] - returned_qty
            row['amount'] = row['amount'] - row['price_unit'] * returned_qty
            if row['product_id'] in delivery_done_dict:
                delivery_done_dict[row['product_id']]['deliveries'].append(row)
            else:
                product = self.env['product.product'].browse(row['product_id'])
                delivery_done_dict[row['product_id']] = {}
                delivery_done_dict[row['product_id']]['product_name'] = product.display_name
                delivery_done_dict[row['product_id']]['deliveries'] = []
                delivery_done_dict[row['product_id']]['deliveries'].append(row)

        return delivery_done_dict

    def get_own_consumption_stock(self, start_date, end_date, operating_unit_id, product_param):
        location_id = self.env['stock.location'].search(
            [('operating_unit_id', '=', operating_unit_id), ('name', '=', 'Stock')],
            limit=1).id

        # through indent
        indent_location_dest_ids = self.env['stock.location'].search(
            [('operating_unit_id', '=', operating_unit_id), ('usage', '=', 'departmental')]).ids

        indent_sql = '''
            SELECT COALESCE(SUM(sm.product_qty), 0) AS total_indent 
            FROM stock_move sm 
            LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
            LEFT JOIN stock_picking_type spt ON sp.picking_type_id = spt.id
            WHERE 
            sm.state = 'done'
            AND sm.product_id IN (%s)
            AND sm.date + interval'6h' BETWEEN '%s'AND '%s'
            AND spt.code = 'internal'
            AND sp.location_id = %s
            AND sp.location_dest_id IN %s
        ''' % (product_param, start_date, end_date, location_id, tuple(indent_location_dest_ids))
        self.env.cr.execute(indent_sql)

        total_indent_qty = 0
        for vals in self.env.cr.dictfetchall():
            total_indent_qty = float(vals['total_indent'])

        sql = '''
                        SELECT 
                             COALESCE(COALESCE(total_consumed_for_production, 0)-COALESCE(total_consumed_for_unbuild, 0), 0) AS consumed_qty
                                FROM (
                                (
                                    SELECT sm.product_id,COALESCE(SUM(sm.product_qty), 0) AS total_consumed_for_production FROM stock_move sm
                                    LEFT JOIN mrp_production mp ON mp.id = sm.raw_material_production_id
                                    WHERE sm.product_id IN %s
                                    AND sm.state = 'done' 
                                    AND sm.date + interval'6h' BETWEEN '%s' AND '%s'
                                    AND mp.operating_unit_id = %s
                                    GROUP BY sm.product_id
                                ) t1
                                FULL JOIN
                                (
                                    SELECT sm.product_id, COALESCE(SUM(sm.product_qty), 0)  AS total_consumed_for_unbuild FROM stock_move sm
                                    LEFT JOIN mrp_unbuild mu ON mu.id = sm.unbuild_id
                                    WHERE sm.product_id IN %s
                                    AND sm.state = 'done' 
                                    AND sm.date + interval'6h' BETWEEN '%s' AND '%s'
                                    AND mu.operating_unit_id = %s
                                    GROUP BY sm.product_id
                                ) t2 ON (t1.product_id = t2.product_id)
                                ) t3
                    ''' % (
            product_param, start_date, end_date, operating_unit_id, product_param, start_date, end_date,
            operating_unit_id)

        self.env.cr.execute(sql)

        datewise_own_consumption_stocklist = []
        consumed_qty = 0
        for vals in self.env.cr.dictfetchall():
            consumed_qty = float(vals['consumed_qty'])
        item = {'consumed_qty': consumed_qty + total_indent_qty}
        datewise_own_consumption_stocklist.append(item)
        return datewise_own_consumption_stocklist

    def get_other_adjustment_received(self, start_date, end_date, operating_unit_id, product_param):
        sql = '''
                        SELECT COALESCE(SUM(product_qty), 0) as adjustment_qty FROM stock_move sm WHERE sm.state = 'done' 
                        AND sm.date BETWEEN DATE('%s')+TIME '00:00:01' AND DATE('%s')+TIME '23:59:59'
                        AND sm.location_id IN (SELECT id FROM stock_location 
                        WHERE usage = 'inventory' 
                        AND 
                        scrap_location = FALSE
                        AND return_location = FALSE
                        )
                        AND sm.location_dest_id IN (SELECT id FROM stock_location WHERE operating_unit_id = %s)
                        AND sm.product_id IN (%s)
                    ''' % (start_date, end_date, operating_unit_id, product_param)

        self.env.cr.execute(sql)
        datewise_other_adjustment_received = []
        for vals in self.env.cr.dictfetchall():
            item = {'adjustment_qty': vals['adjustment_qty']}
            datewise_other_adjustment_received.append(item)
        return datewise_other_adjustment_received

    def get_loss_adjustment_issued(self, start_date, end_date, operating_unit_id, product_param):
        location_id = self.env['stock.location'].search(
            [('operating_unit_id', '=', operating_unit_id), ('name', '=', 'Stock')],
            limit=1).id

        sql = '''
                SELECT COALESCE(SUM(product_qty), 0) as adjustment_qty 
                        FROM stock_move sm 
                            WHERE sm.state = 'done' 
                            AND sm.date BETWEEN DATE('%s')+TIME '00:00:01' AND DATE('%s')+TIME '23:59:59'
                            AND sm.location_id IN (SELECT id FROM stock_location WHERE id IN (%s))
                            AND sm.location_dest_id IN (
                                                    SELECT id FROM stock_location  WHERE usage = 'inventory')
                            AND sm.product_id IN (%s)
            ''' % (start_date, end_date, location_id, product_param)

        self.env.cr.execute(sql)
        datewise_loss_adjustment_issued = []
        for vals in self.env.cr.dictfetchall():
            item = {'adjustment_qty': vals['adjustment_qty']}
            datewise_loss_adjustment_issued.append(item)
        return datewise_loss_adjustment_issued
