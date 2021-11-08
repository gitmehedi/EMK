import datetime

from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class UndeliveredReportXLSX(ReportXlsx):

    def _get_conversion_rate(self):
        conversion_rate_dict = {}
        currencies = self.env['res.currency'].search([('active', '=', True)])
        for cr in currencies:
            to_currency = self.env.user.company_id.currency_id
            from_currency = cr.with_context(date=datetime.datetime.now())
            conversion_rate_dict[cr.name] = to_currency.round(to_currency.rate / from_currency.rate)

        return conversion_rate_dict

    def _get_query_where_clause(self, obj):
        where_str = """WHERE 
                            sp.operating_unit_id=%s AND sp.state NOT IN ('done','cancel')
                            AND DATE(sp.date_done + interval '6h') <= DATE('%s')+time '23:59:59'""" % (obj.operating_unit_id.id, obj.date_today)

        if obj.product_tmpl_id and not obj.product_id:
            product_ids = self.env['product.product'].search([('product_tmpl_id', '=', obj.product_tmpl_id.id), '|', ('active', '=', True), ('active', '=', False)]).ids
            if len(product_ids) > 1:
                where_str += """ AND sm.product_id IN %s""" % (tuple(product_ids),)
            else:
                where_str += """ AND sm.product_id=%s""" % product_ids[0]

        if obj.product_id:
            where_str += """ AND sm.product_id=%s""" % obj.product_id.id

        if obj.partner_id:
            where_str += """ AND so.partner_id=%s""" % obj.partner_id.id

        return where_str

    def _get_undelivered_data(self, obj):
        where_clause = self._get_query_where_clause(obj)
        sql_str = """SELECT
                        DISTINCT sp.origin AS so_no,
                        sm.product_id,
                        so.partner_id,
                        rp.name AS partner_name,
                        so.date_order AS so_date,
                        sol.product_uom_qty AS ordered_qty,
                        sol.qty_delivered AS delivered_qty,
                        (sol.product_uom_qty-sol.qty_delivered) AS undelivered_qty,
                        pm.packaging_mode AS packing_mode,
                        sol.price_unit,
                        sol.currency_id,
                        rc.name AS currency_name,
                        ((sol.product_uom_qty-sol.qty_delivered) * sol.price_unit) AS amount,
                        NULL AS cancel_qty
                    FROM
                        stock_move sm
                        JOIN stock_picking sp ON sp.id=sm.picking_id
                        JOIN stock_picking_type spt ON spt.id=sp.picking_type_id AND spt.code='outgoing'
                        JOIN operating_unit ou ON ou.id=sp.operating_unit_id
                        JOIN product_product pp ON pp.id=sm.product_id
                        JOIN sale_order so ON so.name=sp.origin
                        JOIN sale_order_line sol ON sol.order_id=so.id
                        JOIN res_partner rp ON rp.id=so.partner_id
                        JOIN res_currency rc ON rc.id=sol.currency_id
                        LEFT JOIN product_packaging_mode pm ON pm.id=so.pack_type
                    """ + where_clause + """ ORDER BY so.date_order"""

        undelivered_dict = {}
        conversion_rate_dict = self._get_conversion_rate()
        company_currency_name = self.env.user.company_id.currency_id.name

        self.env.cr.execute(sql_str)
        for row in self.env.cr.dictfetchall():
            if row['currency_name'] != company_currency_name:
                conversion_rate = conversion_rate_dict.get(row['currency_name'], 1.0)
                amount = row['amount'] * conversion_rate
                row['amount'] = amount

            if row['product_id'] in undelivered_dict:
                undelivered_dict[row['product_id']]['sale_orders'].append(row)
            else:
                product = self.env['product.product'].browse(row['product_id'])
                undelivered_dict[row['product_id']] = {}
                undelivered_dict[row['product_id']]['product_name'] = product.display_name
                undelivered_dict[row['product_id']]['sale_orders'] = []
                undelivered_dict[row['product_id']]['sale_orders'].append(row)

        return undelivered_dict

    @staticmethod
    def get_formatted_date(date_str, date_format):
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime(date_format)

    def generate_xlsx_report(self, workbook, data, obj):
        result_data = self._get_undelivered_data(obj)

        """XLSX REPORT"""
        # FORMAT
        bold = workbook.add_format({'bold': True, 'size': 10})
        no_format = workbook.add_format({'num_format': '#,###0.00', 'size': 10, 'border': 1})
        total_format = workbook.add_format({'num_format': '#,###0.00', 'bold': True, 'size': 10, 'border': 1})

        name_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 12})
        address_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10})

        # table header cell format
        th_cell_left = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})
        th_cell_center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})
        th_cell_right = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})

        # table body cell format
        td_cell_left = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'size': 10, 'border': 1})
        td_cell_center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10, 'border': 1})
        td_cell_right = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'size': 10, 'border': 1})

        td_cell_left_bold = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})
        td_cell_center_bold = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})
        td_cell_right_bold = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})

        # WORKSHEET
        sheet = workbook.add_worksheet('Undelivered Report')

        # SET CELL WIDTH
        sheet.set_column(0, 0, 25)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 16)
        sheet.set_column(3, 3, 16)
        sheet.set_column(4, 4, 17)
        sheet.set_column(5, 5, 19)
        sheet.set_column(6, 6, 18)
        sheet.set_column(7, 7, 18)

        last_col = 7

        if not self.env.user.company_id.undelivered_report_factory:
            sheet.set_column(8, 8, 16)
            sheet.set_column(9, 9, 10)
            sheet.set_column(10, 10, 18)
            last_col = 10

        # SHEET HEADER
        conversion_rate_dict = self._get_conversion_rate()
        sheet.merge_range(0, 0, 0, last_col, self.env.user.company_id.name, name_format)
        sheet.merge_range(1, 0, 1, last_col, self.env.user.company_id.street, address_format)
        sheet.merge_range(2, 0, 2, last_col, self.env.user.company_id.street2, address_format)
        sheet.merge_range(3, 0, 3, last_col, self.env.user.company_id.city + '-' + self.env.user.company_id.zip, address_format)
        sheet.merge_range(4, 0, 4, last_col, "Undelivered Report", name_format)

        row = 5
        if not self.env.user.company_id.undelivered_report_factory:
            for key, val in conversion_rate_dict.items():
                if key != self.env.user.company_id.currency_id.name:
                    sheet.merge_range(row, 8, row, 10, key + ": " + str(val), bold)
                    row += 1

        # Filter Block
        partner = obj.partner_id.name or 'All'
        product = obj.product_tmpl_id.display_name or 'All'
        product_variant = obj.product_id.display_name or 'All'

        sheet.merge_range(row, 0, row, 2, "Product: " + product, bold)
        row += 1
        sheet.merge_range(row, 0, row, 2, "Product Variant: " + product_variant, bold)
        sheet.merge_range(row, last_col - 2, row, last_col, "Customer: " + partner, bold)
        row += 1
        sheet.merge_range(row, 0, row, 2, "Operating Unit: " + obj.operating_unit_id.name, bold)
        sheet.merge_range(row, last_col - 2, row, last_col, "Date: " + self.get_formatted_date(obj.date_today, "%d-%m-%Y"), bold)
        row += 1

        # TABLE HEADER
        row, col = row + 1, 0
        sheet.write(row, col, 'Customer Name', th_cell_center)
        sheet.write(row, col + 1, 'SO No.', th_cell_center)
        sheet.write(row, col + 2, 'SO Date', th_cell_center)
        sheet.write(row, col + 3, 'Ordered Qty (MT)', th_cell_center)
        sheet.write(row, col + 4, 'Delivered Qty (MT)', th_cell_center)
        sheet.write(row, col + 5, 'Adjustment/Cancel Qty', th_cell_center)
        sheet.write(row, col + 6, 'Undelivered Qty (MT)', th_cell_center)
        sheet.write(row, col + 7, 'Packing Mode', th_cell_center)

        if not self.env.user.company_id.undelivered_report_factory:
            sheet.write(row, col + 8, 'Unit Price', th_cell_center)
            sheet.write(row, col + 9, 'Currency', th_cell_center)
            sheet.write(row, col + 10, 'Amount (BDT)', th_cell_center)

        # TABLE BODY
        grand_total_amount = 0.0
        row += 1
        for index, value in result_data.items():
            sheet.merge_range(row, col, row, col + last_col, value['product_name'], td_cell_left_bold)
            row += 1

            for rec in value['sale_orders']:
                sheet.write(row, col, rec['partner_name'], td_cell_left)
                sheet.write(row, col + 1, rec['so_no'], td_cell_center)
                sheet.write(row, col + 2, rec['so_date'], td_cell_center)
                sheet.write(row, col + 3, rec['ordered_qty'], no_format)
                sheet.write(row, col + 4, rec['delivered_qty'], no_format)
                sheet.write(row, col + 5, rec['cancel_qty'], no_format)
                sheet.write(row, col + 6, rec['undelivered_qty'], no_format)
                sheet.write(row, col + 7, rec['packing_mode'], td_cell_center)

                if not self.env.user.company_id.undelivered_report_factory:
                    sheet.write(row, col + 8, rec['price_unit'], no_format)
                    sheet.write(row, col + 9, rec['currency_name'], td_cell_center)
                    sheet.write(row, col + 10, rec['amount'], no_format)

                row += 1

            # SUB TOTAL
            sub_total_undelivered_qty = sum(map(lambda x: x['undelivered_qty'], value['sale_orders']))
            sub_total_amount = sum(map(lambda x: x['amount'], value['sale_orders']))
            grand_total_amount += float(sub_total_amount)

            sheet.merge_range(row, col, row, col + 5, 'Sub Total', td_cell_left_bold)
            sheet.write(row, col + 6, sub_total_undelivered_qty, total_format)
            sheet.write(row, col + 7, '', total_format)

            if not self.env.user.company_id.undelivered_report_factory:
                sheet.write(row, col + 8, '', total_format)
                sheet.write(row, col + 9, '', total_format)
                sheet.write(row, col + 10, sub_total_amount, total_format)

            row += 1
            # END

        # GRAND TOTAL
        if not self.env.user.company_id.undelivered_report_factory:
            sheet.merge_range(row, col, row, col + 9, 'Grand Total', td_cell_left_bold)
            sheet.write(row, col + 10, grand_total_amount, total_format)
        # END


UndeliveredReportXLSX('report.delivery_reports.undelivered_report_xlsx', 'undelivered.report.wizard', parser=report_sxw.rml_parse)
