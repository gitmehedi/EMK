from odoo import fields, models, api


class LoanDataUtility(models.TransientModel):
    _name = 'loan.data.utility'
    _description = 'Loan Data Utility'

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

    def get_loan_lending_stock_issued(self, start_date, end_date, operating_unit_id, product_param, is_transfer):
        # loan lending issued
        customer_location_for_loan_lending = self.env['stock.location'].search(
            [('can_loan_request', '=', True), ('usage', '=', 'customer')], limit=1).id
        if not customer_location_for_loan_lending:
            customer_location_for_loan_lending = 'NULL'
        loan_lending_picking_type = self.env['stock.picking.type'].search(
            [('operating_unit_id', '=', operating_unit_id), ('code', '=', 'loan_outgoing'),
             ('default_location_dest_id', '=', customer_location_for_loan_lending)], limit=1).id
        if not loan_lending_picking_type:
            loan_lending_picking_type = 'NULL'
        stock_utility = self.env['stock.utility']

        location_id = self.env['stock.location'].search(
            [('operating_unit_id', '=', operating_unit_id), ('name', '=', 'Stock')],
            limit=1).id
        location_main_stock = self.env['stock.location'].browse(location_id)

        sql = '''
                SELECT sm.id,COALESCE(sm.product_qty, 0) as loan_lending_issued
                FROM stock_move sm
                    LEFT JOIN stock_picking sp ON sm.picking_id = sp.id 
                    LEFT JOIN item_loan_lending ill ON ill.name = sp.origin 
                        WHERE sm.date BETWEEN DATE('%s')+TIME '00:00:01' AND DATE('%s')+TIME '23:59:59'
                            AND sm.state = 'done' 
                            AND sm.product_id IN (%s)
                            AND sm.location_id = %s
                            AND sm.location_dest_id = %s
                            AND sp.picking_type_id = %s
                            AND sp.transfer_type = 'loan'
                        AND ill.is_transfer = %s

                ''' % (
            start_date, end_date, product_param, location_main_stock.id, customer_location_for_loan_lending,
            loan_lending_picking_type, is_transfer)

        self.env.cr.execute(sql)
        datewise_loan_lending = 0.0
        for vals in self.env.cr.dictfetchall():
            returned_qty = self.get_total_return_qty_move(vals['id'])
            datewise_loan_lending = datewise_loan_lending + float(vals['loan_lending_issued']) - returned_qty

            # issued after loan borrowing
        supplier_loc_for_loan_lending = self.env['stock.location'].search(
            [('can_loan_request', '=', True), ('usage', '=', 'supplier')], limit=1).id
        if not supplier_loc_for_loan_lending:
            supplier_loc_for_loan_lending = 'NULL'
        issue_after_loan_borrow_picking_type = self.env['stock.picking.type'].search(
            [('operating_unit_id', '=', operating_unit_id), ('code', '=', 'loan_outgoing'),
             ('default_location_dest_id', '=', supplier_loc_for_loan_lending)], limit=1).id

        if not issue_after_loan_borrow_picking_type:
            issue_after_loan_borrow_picking_type = 'NULL'
        sql2 = '''
            SELECT sm.id,COALESCE(sm.product_qty, 0) as issued_after_loan_borrowing
                FROM stock_move sm
                LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
                 WHERE sm.date BETWEEN DATE('%s')+TIME '00:00:01' AND DATE('%s')+TIME '23:59:59'
                            AND sm.state = 'done' 
                            AND sm.product_id IN (%s)
                            AND sm.location_id = %s
                            AND sm.location_dest_id = %s
                            AND sp.picking_type_id = %s
                            AND sp.transfer_type = 'loan'
            ''' % (
            start_date, end_date, product_param, location_main_stock.id, supplier_loc_for_loan_lending,
            issue_after_loan_borrow_picking_type)

        self.env.cr.execute(sql2)
        datewise_issued_after_loan_borrowing = 0.0
        for vals in self.env.cr.dictfetchall():
            returned_qty = self.get_total_return_qty_move(vals['id'])
            datewise_issued_after_loan_borrowing = datewise_issued_after_loan_borrowing + float(
                vals['issued_after_loan_borrowing']) - returned_qty

        datewise_loan_lending_issued = []
        if is_transfer:
            item = {'loan_lending_qty': datewise_loan_lending}
        else:
            item = {'loan_lending_qty': datewise_loan_lending + datewise_issued_after_loan_borrowing}
        datewise_loan_lending_issued.append(item)
        return datewise_loan_lending_issued

    def get_loan_stock_received(self, start_date, end_date, operating_unit_id, product_param, is_transfer):
        vendor_location_for_loan_borrowing = self.env['stock.location'].search(
            [('can_loan_request', '=', True), ('usage', '=', 'supplier')], limit=1).id
        if not vendor_location_for_loan_borrowing:
            vendor_location_for_loan_borrowing = 'NULL'
        customer_location_for_loan_lending = self.env['stock.location'].search(
            [('can_loan_request', '=', True), ('usage', '=', 'customer')], limit=1).id
        if not customer_location_for_loan_lending:
            customer_location_for_loan_lending = 'NULL'
        input_location_id = self.env['stock.location'].search(
            [('operating_unit_id', '=', operating_unit_id), ('name', '=', 'Input')],
            limit=1).id
        if not input_location_id:
            input_location_id = 'NULL'
        qc_location_id = self.env['stock.location'].search(
            [('operating_unit_id', '=', operating_unit_id), ('name', '=', 'Quality Control')],
            limit=1).id
        if not qc_location_id:
            qc_location_id = 'NULL'
        location_id = self.env['stock.location'].search(
                [('operating_unit_id', '=', operating_unit_id), ('name', '=', 'Stock')],
                limit=1).id
        location_main_stock = self.env['stock.location'].browse(location_id)
        loan_borrowing_picking_type = self.env['stock.picking.type'].search(
            [('operating_unit_id', '=', operating_unit_id), ('code', '=', 'incoming'),
             ('default_location_src_id', '=', vendor_location_for_loan_borrowing),
             ('default_location_dest_id', '=', input_location_id)], limit=1).id
        if not loan_borrowing_picking_type:
            loan_borrowing_picking_type = 'NULL'
        loan_lending_return_picking_type = self.env['stock.picking.type'].search(
            [('operating_unit_id', '=', operating_unit_id), ('code', '=', 'incoming'),
             ('default_location_src_id', '=', customer_location_for_loan_lending),
             ('default_location_dest_id', '=', input_location_id)], limit=1).id
        if not loan_lending_return_picking_type:
            loan_lending_return_picking_type = 'NULL'

        internal_picking_type = self.env['stock.picking.type'].search(
            [('operating_unit_id', '=', operating_unit_id), ('code', '=', 'internal'),
             ('default_location_src_id', '=', location_main_stock.id),
             ('default_location_dest_id', '=', location_main_stock.id)], limit=1).id
        if not internal_picking_type:
            internal_picking_type = 'NULL'
        lenders_to_input_sql = '''
                SELECT sp.transfer_type, sp.receive_type,sp.origin
                FROM stock_move sm
                    LEFT JOIN stock_picking sp ON sm.picking_id = sp.id 
                    LEFT JOIN item_borrowing ib ON ib.name = sp.origin
    					WHERE sm.date BETWEEN DATE('%s')+TIME '00:00:01'
                            AND DATE('%s')+TIME '23:59:59'
                            AND sm.state ='done'
                            AND sm.product_id IN (%s)
                            AND sm.location_id = %s
                            AND sm.location_dest_id = %s
                            AND sm.picking_type_id = %s
                            AND ib.is_transfer = %s

                ''' % (
            start_date, end_date, product_param, vendor_location_for_loan_borrowing, input_location_id,
            loan_borrowing_picking_type, is_transfer)

        self.env.cr.execute(lenders_to_input_sql)
        datewise_loan_borrowing_received = 0.0
        for vals in self.env.cr.dictfetchall():
            if vals['transfer_type'] == 'loan' and vals['receive_type'] == 'loan':
                to_stock_sql = '''
                            SELECT sm.id,COALESCE(sm.product_qty, 0) as loan_borrowing_received
                            FROM stock_move sm
                            LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
                            WHERE sp.origin = '%s'
                                    AND sm.state = 'done'
                                    AND sm.location_id = %s
                                    AND sm.location_dest_id = %s

                    ''' % (vals['origin'], qc_location_id, location_main_stock.id)
                self.env.cr.execute(to_stock_sql)
                loan_borrowing_received = 0.0
                for vals in self.env.cr.dictfetchall():
                    returned_qty = self.get_total_return_qty_move(vals['id'])
                    loan_borrowing_received = loan_borrowing_received + float(
                        vals['loan_borrowing_received']) - returned_qty
                datewise_loan_borrowing_received = datewise_loan_borrowing_received + loan_borrowing_received

        # receive after loan lending

        receive_after_loan_lending_sql = '''
                    SELECT sm.id,COALESCE(sm.product_qty, 0) as received_after_loan_lending FROM stock_move sm 
                        LEFT JOIN stock_picking sp ON sm.picking_id = sp.id 
                        WHERE sm.state = 'done'
                        AND  sm.date BETWEEN DATE('%s')+TIME '00:00:01'
                        AND DATE('%s')+TIME '23:59:59'
                        AND sm.product_id IN (%s)
                        AND sp.picking_type_id = %s
                        AND sp.transfer_type = 'receive'
                        AND sp.receive_type = 'loan'
                        AND sp.location_id = %s
                        AND sp.location_dest_id = %s
            ''' % (start_date, end_date, product_param, internal_picking_type, qc_location_id,
                   location_main_stock.id)
        self.env.cr.execute(receive_after_loan_lending_sql)
        datewise_received_after_loan_lending = 0.0
        for vals in self.env.cr.dictfetchall():
            returned_qty = self.get_total_return_qty_move(vals['id'])
            datewise_received_after_loan_lending = datewise_received_after_loan_lending + float(
                vals['received_after_loan_lending']) - returned_qty
        datewise_loan_borrowing = []

        if is_transfer:
            item = {'loan_borrowing_qty': datewise_loan_borrowing_received}
        else:
            item = {'loan_borrowing_qty': datewise_loan_borrowing_received + datewise_received_after_loan_lending}

        datewise_loan_borrowing.append(item)
        return datewise_loan_borrowing

    def get_received_from_other_unit(self, start_date, end_date, operating_unit_id, product_param, is_transfer):
        input_location_id = self.env['stock.location'].search(
            [('operating_unit_id', '=', operating_unit_id), ('name', '=', 'Input')],
            limit=1).id
        if not input_location_id:
            input_location_id = 'NULL'

        operating_unit_obj = self.env['operating.unit'].browse(operating_unit_id)
        transit_location_id = self.env['stock.location'].search(
            [('company_id', '=', operating_unit_obj.company_id.id), ('usage', '=', 'transit'),
             ('can_operating_unit_transfer', '=', True)], limit=1).id

        if not transit_location_id:
            transit_location_id = 'NULL'
        qc_location_id = self.env['stock.location'].search(
            [('operating_unit_id', '=', operating_unit_id), ('name', '=', 'Quality Control')],
            limit=1).id
        location_id = self.env['stock.location'].search(
                [('operating_unit_id', '=', operating_unit_id), ('name', '=', 'Stock')],
                limit=1).id
        location_main_stock = self.env['stock.location'].browse(location_id)

        origin_sql = '''
                SELECT sm.origin FROM stock_move sm
                    LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
                    LEFT JOIN item_borrowing ib ON ib.name = sp.origin
                    LEFT JOIN stock_picking_type spt ON sp.picking_type_id = spt.id
                         WHERE sm.date BETWEEN DATE('%s')+TIME '00:00:01'
                            AND DATE('%s')+TIME '23:59:59'
                            AND sm.state ='done'
                            AND sm.product_id IN (%s)   
                            AND sp.location_dest_id = %s
                            AND spt.code = 'operating_unit_transfer'
                            AND spt.default_location_src_id = %s
                            AND spt.default_location_dest_id = %s
                            AND ib.is_transfer = %s
                
            ''' % (
            start_date, end_date, product_param, input_location_id, transit_location_id, input_location_id, is_transfer)

        self.env.cr.execute(origin_sql)
        total_received_qty = 0.0
        total_returned_qty = 0.0
        for vals in self.env.cr.dictfetchall():
            origin = vals['origin']
            received_item_sql = '''
                    SELECT sm.id,COALESCE(sm.product_qty, 0) as received_item
                    FROM stock_move sm
                    LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
                    WHERE sp.origin = '%s'
                            AND sm.state = 'done'
                            AND sm.location_id = %s
                            AND sm.location_dest_id = %s
                                ''' % (origin, qc_location_id, location_main_stock.id)

            self.env.cr.execute(received_item_sql)
            for values in self.env.cr.dictfetchall():
                total_received_qty = total_received_qty + float(values['received_item'])

            return_sql = '''
                    SELECT sm.id
                    FROM stock_move sm
                    LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
                    WHERE sp.origin = '%s' AND sm.state = 'done'
                                ''' % (origin)
            self.env.cr.execute(return_sql)
            return_qty = 0.0
            for vals in self.env.cr.dictfetchall():
                returned_qty = self.get_total_return_qty_move(vals['id'])
                return_qty = return_qty + returned_qty

            total_returned_qty = total_returned_qty + return_qty
        # need to deduct return qty from here
        datewise_item_receiving = []
        item = {'item_receiving_qty': total_received_qty - total_returned_qty}
        datewise_item_receiving.append(item)
        return datewise_item_receiving

    def get_issued_to_other_unit_stock(self, start_date, end_date, operating_unit_id, product_param, is_transfer):
        operating_unit_obj = self.env['operating.unit'].browse(operating_unit_id)
        transit_location_id = self.env['stock.location'].search(
            [('company_id', '=', operating_unit_obj.company_id.id), ('usage', '=', 'transit'),
             ('can_operating_unit_transfer', '=', True)], limit=1).id
        if not transit_location_id:
            transit_location_id = 'NULL'

        location_id = self.env['stock.location'].search(
                [('operating_unit_id', '=', operating_unit_id), ('name', '=', 'Stock')],
                limit=1).id
        location_main_stock = self.env['stock.location'].browse(location_id)

        sent_item_sql = '''
            SELECT sm.id,COALESCE(sm.product_qty, 0) as sent_item FROM stock_move sm
                LEFT JOIN stock_picking sp ON sm.picking_id = sp.id 
                LEFT JOIN item_loan_lending ill ON ill.name = sp.origin 
                LEFT JOIN stock_picking_type spt ON sp.picking_type_id = spt.id
                WHERE sm.date BETWEEN DATE('%s')+TIME '00:00:01'
                            AND DATE('%s')+TIME '23:59:59'
                            AND sm.state ='done'
                            AND sm.product_id IN (%s)   
                AND sm.location_id = %s
                AND sm.location_dest_id = %s 
                AND spt.code = 'operating_unit_transfer'
                AND spt.default_location_src_id = %s 
                AND spt.default_location_dest_id = %s
                AND ill.is_transfer = %s
        
        ''' % (start_date,end_date,product_param,location_main_stock.id, transit_location_id, location_main_stock.id, transit_location_id, is_transfer)

        self.env.cr.execute(sent_item_sql)
        datewise_sent_item = 0.0
        for vals in self.env.cr.dictfetchall():
            returned_qty = self.get_total_return_qty_move(vals['id'])
            datewise_sent_item = datewise_sent_item + float(vals['sent_item']) - returned_qty

        datewise_item_sending = []
        item = {'item_send_qty': datewise_sent_item}
        datewise_item_sending.append(item)
        return datewise_item_sending
