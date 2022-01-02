from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class ProductionReportXLSX(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, obj):
        ReportUtility = self.env['report.utility']
        # data structure
        report_data = {
            'product_name': 'calcium carbonate filler',
            'production_qty': 100,
            'delivery_qty': 120,
            'consumable_product_lines': [
                {'product_id': 16255, 'product_name': 'Raw-1', 'quantity_done_store': 100, 'uom_id': 5, 'uom': 'Kg'},
                {'product_id': 16255, 'product_name': 'Raw-1', 'quantity_done_store': 100, 'uom_id': 5, 'uom': 'Kg'},
                {'product_id': 16255, 'product_name': 'Raw-1', 'quantity_done_store': 100, 'uom_id': 5, 'uom': 'Kg'},
                {'product_id': 16255, 'product_name': 'Raw-1', 'quantity_done_store': 100, 'uom_id': 5, 'uom': 'Kg'},
                {'product_id': 16255, 'product_name': 'Raw-1', 'quantity_done_store': 100, 'uom_id': 5, 'uom': 'Kg'},
                {'product_id': 16255, 'product_name': 'Raw-1', 'quantity_done_store': 100, 'uom_id': 5, 'uom': 'Kg'},
                {'product_id': 16255, 'product_name': 'Raw-1', 'quantity_done_store': 100, 'uom_id': 5, 'uom': 'Kg'}
            ]
        }

        report_name = 'Production Report'
        sheet = workbook.add_worksheet(report_name)
        sheet.set_column(0, 1, 14)
        sheet.set_column(2, 2, 46)
        sheet.set_column(5, 5, 24)
        sheet.set_column(3, 4, 14)
        # FORMAT
        bold = workbook.add_format({'bold': True, 'size': 10})
        name_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 8})
        name_format_left = workbook.add_format({'align': 'left', 'bold': True, 'size': 8})
        header_format_left = workbook.add_format({'align': 'left', 'bg_color': '#78B0DE', 'bold': True, 'size': 8})
        normal_format_left = workbook.add_format({'align': 'left', 'size': 8})
        normal_format_left_comma_separator = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'size': 8})

        merged_format_center = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'center', 'valign': 'vcenter', 'size': 8})
        address_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 7})
        no_format = workbook.add_format({'num_format': '#,###0.00', 'size': 7, 'border': 1})
        total_format = workbook.add_format({'num_format': '#,###0.00', 'bold': True, 'size': 7, 'border': 1})

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

        sql = '''
        
           SELECT
               t1.product_id,
               t1.type as production_type,
               t2.type as unbuild_type,
               t1.product_name,
               t1.product_uom,
               t1.name,
               t1.cost,
               COALESCE(COALESCE(t1.total_qty, 0) - COALESCE(t2.total_qty, 0), 0) as after_total_qty,
               COALESCE(t1.total_qty, 0) as production_qty,
               COALESCE(t2.total_qty, 0) as unbuild_qty 
            FROM
               (
                  SELECT
                     sm.product_id,
                     pt.name AS product_name,
                     CASE
                        WHEN
                           sm.product_id = mp.product_id 
                        THEN
                           'produce' 
                        ELSE
                           'consume' 
                     END
                     AS type, sm.product_uom, uom.name, SUM(sm.quantity_done_store) AS total_qty,
                      Coalesce((SELECT ph.cost
                                             FROM   product_price_history ph
                                             WHERE  ph.datetime + interval'6h' <= DATE('%s')+TIME '00:00:01'
                                                    AND  sm.product_id = ph.product_id
                                             ORDER  BY ph.datetime DESC,ph.id DESC
                                             LIMIT  1), 0) as cost  
                  FROM
                     stock_move sm 
                     JOIN
                        mrp_production mp 
                        ON mp.id = sm.raw_material_production_id 
                        OR mp.id = sm.production_id 
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
                     AND mp.date_planned_start + interval'6h' BETWEEN DATE('%s')+TIME '00:00:01' AND DATE('%s')+TIME '23:59:59' 
                     AND sm.state = 'done' 
                     AND mp.operating_unit_id = %s
                  GROUP BY
                     sm.product_id, mp.product_id, pt.name, sm.product_uom, uom.name 			
                  ORDER BY
                     sm.product_id 
               )
               t1 
               FULL JOIN
                  (
                     SELECT
                        sm.product_id,
                        pt.name AS product_name,
                        CASE
                           WHEN
                              sm.product_id = mu.product_id 
                           THEN
                              'produce' 
                           ELSE
                              'consume' 
                        END
                        AS type, sm.product_uom, uom.name, SUM(sm.quantity_done_store) AS total_qty,
                          Coalesce((SELECT ph.cost
                                             FROM   product_price_history ph
                                             WHERE  ph.datetime + interval'6h' <= DATE('%s')+TIME '00:00:01'
                                                    AND  sm.product_id = ph.product_id
                                             ORDER  BY ph.datetime DESC,ph.id DESC
                                             LIMIT  1), 0)  as cost
                  
                         
                     FROM
                        stock_move sm 
                        JOIN
                           mrp_unbuild mu 
                           on sm.unbuild_id = mu.id 
                           or sm.consume_unbuild_id = mu.id 
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
                        sm.product_id, mu.product_id, pt.name, sm.product_uom, uom.name 
                     ORDER BY
                        sm.product_id 
                  )
                  t2 
                  ON (t1.product_id = t2.product_id);
        ''' % (obj.date_from, obj.product_id.id, obj.date_from, obj.date_to, obj.operating_unit_id.id, obj.date_from,
               obj.date_from, obj.date_to,
               obj.product_id.id, obj.operating_unit_id.id)

        self.env.cr.execute(sql)
        row_no = 9
        initial_row = row_no
        production_total_qty = 0
        cost_sum = 0

        for vals in self.env.cr.dictfetchall():
            if not vals['production_type'] == 'produce':
                sheet.write(row_no, 2, vals['product_name'], normal_format_left)
                sheet.write(row_no, 3, vals['after_total_qty'], normal_format_left_comma_separator)
                sheet.write(row_no, 4, vals['name'], normal_format_left)
                if self.env.user.has_group('account.group_account_user'):
                    sheet.write(row_no, 5, vals['cost'], normal_format_left_comma_separator)
                    sheet.write(row_no, 6, vals['after_total_qty'] * vals['cost'], normal_format_left_comma_separator)
                row_no = row_no + 1
                cost_sum = cost_sum + vals['after_total_qty'] * vals['cost']
            if vals['production_type'] == 'produce':
                production_total_qty = vals['after_total_qty']
        if initial_row == row_no:
            sheet.merge_range(initial_row, 0, row_no, 0, production_total_qty, merged_format_center)
        else:
            sheet.merge_range(initial_row, 0, row_no - 1, 0, production_total_qty, merged_format_center)

        delivery_quantity_sql = '''
            SELECT
               l.product_id,
               uom.name,
               CASE
                  WHEN
                     i.type = 'out_invoice' 
                  THEN
                     CASE
                        WHEN
                           COALESCE(p.ratio_in_percentage, 0) = 0 
                        THEN
                           COALESCE(SUM(aml.quantity), 0) 
                        ELSE
            (p.ratio_in_percentage * COALESCE(SUM(aml.quantity), 0) / 100) 
                     END
                     ELSE
                        0 
               END
               as quantity 
            FROM
               account_move_line aml 
               JOIN
                  account_move mv 
                  ON mv.id = aml.move_id 
               JOIN
                  account_invoice i 
                  ON i.move_id = mv.id 
                  AND i.type IN 
                  (
                     'out_invoice', 'out_refund' 
                  )
               JOIN
                  account_invoice_line l 
                  ON l.invoice_id = i.id 
               JOIN
                  product_product p 
                  ON p.id = l.product_id 
               LEFT JOIN
                  product_uom uom 
                  ON uom.id = l.uom_id 
            where
               p.id = %s 
               AND aml.date BETWEEN '%s' AND '%s' 
               AND aml.operating_unit_id = %s 
            GROUP BY
               l.product_id, uom.name , p.ratio_in_percentage, i.type
        
        ''' % (obj.product_id.id, obj.date_from, obj.date_to, obj.operating_unit_id.id)
        self.env.cr.execute(delivery_quantity_sql)
        delivery_quantity = 0
        for vals in self.env.cr.dictfetchall():
            delivery_quantity = vals['quantity']

        if initial_row == row_no:
            sheet.merge_range(initial_row, 1, row_no, 1, delivery_quantity, merged_format_center)
        else:
            sheet.merge_range(initial_row, 1, row_no - 1, 1, delivery_quantity, merged_format_center)

        if self.env.user.has_group('account.group_account_user'):
            sheet.write(row_no + 1, 5, 'Total Cost of Raw Materials', normal_format_left)
            sheet.write(row_no + 1, 6, cost_sum, normal_format_left_comma_separator)

            sheet.write(row_no + 2, 5, 'Cost for ' + str(production_total_qty) + ' MT', normal_format_left_comma_separator)
            sheet.write(row_no + 2, 6, cost_sum, normal_format_left_comma_separator)

            sheet.write(row_no + 3, 5, 'Unit Cost',
                        normal_format_left_comma_separator)
            if production_total_qty > 0:
                sheet.write(row_no + 3, 6, cost_sum/production_total_qty, normal_format_left_comma_separator)
            else:
                sheet.write(row_no + 3, 6, '', normal_format_left_comma_separator)
        data['name'] = 'Production Report'


ProductionReportXLSX('report.mrp_reports.production_report_xlsx',
                     'production.report.wizard', parser=report_sxw.rml_parse)
