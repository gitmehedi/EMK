from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class ProductionReportXLSX(ReportXlsx):

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

    def generate_xlsx_report(self, workbook, data, obj):
        ReportUtility = self.env['report.utility']
        report_name = 'Production Report'
        sheet = workbook.add_worksheet(report_name)
        sheet.set_column(0, 1, 14)
        sheet.set_column(2, 2, 46)
        sheet.set_column(5, 6, 24)
        sheet.set_column(3, 4, 14)
        # FORMAT
        bold = workbook.add_format({'bold': True, 'size': 10})
        name_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 8})
        name_format_left = workbook.add_format({'align': 'left', 'bold': True, 'size': 8})
        header_format_left = workbook.add_format({'align': 'left', 'bg_color': '#d7ecfa', 'bold': True, 'size': 8})
        normal_format_left = workbook.add_format({'align': 'left', 'size': 8})
        normal_format_left_comma_separator = workbook.add_format(
            {'num_format': '#,###0.0000', 'align': 'left', 'size': 8})

        merged_format_center = workbook.add_format(
            {'num_format': '#,###0.0000', 'align': 'center', 'valign': 'vcenter', 'size': 8})
        address_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 7})

        # SHEET HEADER
        if self.env.user.has_group('account.group_account_user'):
            sheet.merge_range(0, 0, 0, 6, self.env.user.company_id.name, name_format)
            sheet.merge_range(1, 0, 1, 6, self.env.user.company_id.street, address_format)
            sheet.merge_range(2, 0, 2, 6, self.env.user.company_id.street2, address_format)
            sheet.merge_range(3, 0, 3, 6, self.env.user.company_id.city + '-' + self.env.user.company_id.zip,
                              address_format)
        else:
            sheet.merge_range(0, 0, 0, 4, self.env.user.company_id.name, name_format)
            sheet.merge_range(1, 0, 1, 4, self.env.user.company_id.street, address_format)
            sheet.merge_range(2, 0, 2, 4, self.env.user.company_id.street2, address_format)
            sheet.merge_range(3, 0, 3, 4, self.env.user.company_id.city + '-' + self.env.user.company_id.zip,
                              address_format)
        if self.env.user.has_group('account.group_account_user'):
            sheet.merge_range(4, 0, 4, 6, "Production Report", name_format)
        else:
            sheet.merge_range(4, 0, 4, 4, "Production Report", name_format)
        product_name = obj.product_id.name_get()[0][1]

        sheet.merge_range(5, 0, 5, 2, "Product : " + product_name, name_format_left)
        if self.env.user.has_group('account.group_account_user'):
            sheet.merge_range(5, 3, 5, 6, "Date : " + ReportUtility.get_date_from_string(
                obj.date_from) + ' to ' + ReportUtility.get_date_from_string(obj.date_to), name_format_left)
        else:

            sheet.merge_range(5, 3, 5, 4, "Date : " + ReportUtility.get_date_from_string(
                obj.date_from) + ' to ' + ReportUtility.get_date_from_string(obj.date_to), name_format_left)

        sheet.merge_range(6, 0, 6, 2, "Operating Unit : " + obj.operating_unit_id.name, name_format_left)

        sheet.write(8, 0, "Total Production (MT)", header_format_left)
        sheet.write(8, 1, "Total Delivery(MT)", header_format_left)

        sheet.write(8, 2, "Raw / Packing Materials", header_format_left)
        sheet.write(8, 3, "Quantity", header_format_left)
        sheet.write(8, 4, "Unit", header_format_left)

        if self.env.user.has_group('account.group_account_user'):
            sheet.write(8, 5, "Unit Cost", header_format_left)
            sheet.write(8, 6, "Total Cost", header_format_left)

        consumed_sql = '''
                SELECT
                   t1.product_id,
                   t1.product_name,
                   t1.product_uom,
                   t1.name,
                    COALESCE(t1.amount, 0)  as t1_amount,
				  COALESCE(t2.amount, 0)  as t2_amount,
                   t1.avg_cost,
                   COALESCE(COALESCE(t1.total_qty, 0) - COALESCE(t2.total_qty, 0), 0) as after_total_qty,
                   COALESCE(t1.total_qty, 0) as production_qty,
                   COALESCE(t2.total_qty, 0) as unbuild_qty 
                FROM
                   (
                      SELECT
                         sm.product_id,
                         AVG(sm.price_unit) as avg_cost,
                         SUM(sm.quantity_done_store * sm.price_unit) AS amount,
                         pt.name AS product_name,
                         sm.product_uom,
                         uom.name,
                         SUM(sm.quantity_done_store) AS total_qty 
                      FROM
                         stock_move sm 
                         JOIN
                            mrp_production mp 
                            ON mp.id = sm.raw_material_production_id 
                         LEFT JOIN
                            product_uom uom 
                            ON uom.id = sm.product_uom 
                         LEFT JOIN
                            product_product pp 
                            ON pp.id = sm.product_id 
                         LEFT JOIN
                            product_template pt 
                            ON pt.id = pp.product_tmpl_id 
                      WHERE
                         mp.product_id = %s 
                         AND mp.state = 'done' 
                         AND mp.date_planned_start + interval'6h' BETWEEN DATE('%s') + TIME '00:00:01' AND DATE('%s') + TIME '23:59:59' 
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
                            -SUM(sm.quantity_done_store * sm.price_unit) AS amount,
                            sm.product_uom,
                            uom.name,
                            SUM(sm.quantity_done_store) AS total_qty 
                         FROM
                            stock_move sm 
                            JOIN
                               mrp_unbuild mu 
                               on sm.unbuild_id = mu.id 
                            LEFT JOIN
                               product_uom uom 
                               ON uom.id = sm.product_uom 
                            LEFT JOIN
                               product_product pp 
                               ON pp.id = sm.product_id 
                            LEFT JOIN
                               product_template pt 
                               ON pt.id = pp.product_tmpl_id 
                         WHERE
                            sm.state = 'done' 
                            AND mu.state = 'done' 
                            AND mu.date_unbuild BETWEEN '%s' AND '%s' 
                            and mu.product_id = %s 
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
        ''' % (obj.product_id.id, obj.date_from, obj.date_to, obj.operating_unit_id.id, obj.date_from, obj.date_to,
               obj.product_id.id, obj.operating_unit_id.id)

        self.env.cr.execute(consumed_sql)
        row_no = 9
        initial_row = row_no

        cost_sum = 0.0

        for vals in self.env.cr.dictfetchall():
            # if not vals['production_type'] == 'produce':
            product_name = ''
            if vals['product_id']:
                product_product_obj = self.env['product.product'].browse(vals['product_id'])
                product_name = product_product_obj.name_get()[0][1]
            sheet.write(row_no, 2, product_name, normal_format_left)
            sheet.write(row_no, 3, vals['after_total_qty'], normal_format_left_comma_separator)
            sheet.write(row_no, 4, vals['name'], normal_format_left)
            if self.env.user.has_group('account.group_account_user'):
                sheet.write(row_no, 5, (vals['t1_amount'] + vals['t2_amount'])/vals['after_total_qty'], normal_format_left_comma_separator)
                sheet.write(row_no, 6, vals['t1_amount'] + vals['t2_amount'],
                            normal_format_left_comma_separator)
            row_no = row_no + 1
            if vals['t1_amount'] or vals['t2_amount']:
                cost_sum = cost_sum + vals['t1_amount'] + vals['t2_amount']

        production_sql = '''
                SELECT t1.product_id,t1.product_name,t1.product_uom,t1.name,t1.avg_cost,
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
                         AND mp.date_planned_start + interval'6h' BETWEEN DATE('%s') + TIME '00:00:01' AND DATE('%s') + TIME '23:59:59' 
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
                            AND mu.date_unbuild BETWEEN '%s' AND '%s' 
                            and mu.product_id = %s 
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
        ''' % (obj.product_id.id, obj.date_from, obj.date_to, obj.operating_unit_id.id, obj.date_from, obj.date_to,
               obj.product_id.id, obj.operating_unit_id.id)

        self.env.cr.execute(production_sql)
        production_total_qty = 0
        for vals in self.env.cr.dictfetchall():
            production_total_qty = vals['after_total_qty']
        if initial_row == row_no:
            sheet.merge_range(initial_row, 0, row_no, 0, production_total_qty, merged_format_center)
        elif row_no - initial_row == 1:
            sheet.write(initial_row, 0, production_total_qty, normal_format_left_comma_separator)
        # sheet.merge_range(initial_row, 0, row_no, 0, production_total_qty, merged_format_center)
        else:
            sheet.merge_range(initial_row, 0, row_no - 1, 0, production_total_qty, merged_format_center)

        result_data = self._get_delivery_done(obj.operating_unit_id.id, obj.date_from, obj.date_to, obj.product_id.id)
        delivery_quantity = 0
        for index, value in result_data.items():
            delivery_quantity = sum(map(lambda x: x['delivered_qty'], value['deliveries']))

        if initial_row == row_no:
            sheet.merge_range(initial_row, 1, row_no, 1, delivery_quantity, merged_format_center)

        elif row_no - initial_row == 1:
            sheet.write(initial_row, 1, delivery_quantity, normal_format_left_comma_separator)
        else:
            sheet.merge_range(initial_row, 1, row_no - 1, 1, delivery_quantity, merged_format_center)

        if self.env.user.has_group('account.group_account_user'):
            sheet.write(row_no + 1, 5, 'Total Cost of Raw Materials', normal_format_left)
            sheet.write(row_no + 1, 6, cost_sum, normal_format_left_comma_separator)

            sheet.write(row_no + 2, 5, 'Cost for ' + str(production_total_qty) + ' MT',
                        normal_format_left_comma_separator)
            sheet.write(row_no + 2, 6, cost_sum, normal_format_left_comma_separator)

            sheet.write(row_no + 3, 5, 'Unit Cost',
                        normal_format_left_comma_separator)
            if production_total_qty > 0:
                sheet.write(row_no + 3, 6, cost_sum / production_total_qty, normal_format_left_comma_separator)
            else:
                sheet.write(row_no + 3, 6, '', normal_format_left_comma_separator)
        data['name'] = 'Production Report'


ProductionReportXLSX('report.mrp_reports.production_report_xlsx',
                     'production.report.wizard', parser=report_sxw.rml_parse)
