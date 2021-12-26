import datetime

from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class DeliveryReportXLSX(ReportXlsx):

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
                            sp.operating_unit_id=%s 
                            AND DATE(sp.date_done + interval '6h') BETWEEN DATE('%s')+time '00:00' AND DATE('%s')+time '23:59:59'""" % (obj.operating_unit_id.id, obj.date_from, obj.date_to)

        if obj.product_tmpl_id and not obj.product_id:
            product_ids = self.env['product.product'].search([('product_tmpl_id', '=', obj.product_tmpl_id.id), '|', ('active', '=', True), ('active', '=', False)]).ids
            if len(product_ids) > 1:
                where_str += """ AND spo.product_id IN %s""" % (tuple(product_ids),)
            else:
                where_str += """ AND spo.product_id=%s""" % product_ids[0]

        if obj.product_id:
            where_str += """ AND spo.product_id=%s""" % obj.product_id.id

        if obj.partner_id:
            where_str += """ AND so.partner_id=%s""" % obj.partner_id.id

        return where_str

    def _get_delivery_returned(self, obj):
        delivery_returned_list = []
        where_clause = self._get_query_where_clause(obj)
        sql_str = """SELECT
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
        """ + where_clause + """ AND sp.state!='cancel' GROUP BY sp.origin"""

        self.env.cr.execute(sql_str)
        for row in self.env.cr.dictfetchall():
            delivery_returned_list.append(row)

        return delivery_returned_list

    def _get_delivery_done(self, obj):
        where_clause = self._get_query_where_clause(obj)
        sql_str = """SELECT
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
                    """ + where_clause + """ AND sp.state='done'
                    GROUP BY
                        sp.name,spo.product_id,pt.name,so.partner_id,rp.name,sp.origin,so.date_order,
                        sp.date_done,sp.vat_challan_id,lc.name,pm.packaging_mode,spo.qty_done,sol.price_unit,sol.currency_id,rc.name
                    ORDER BY 
                        sp.date_done
        """

        delivery_done_dict = {}
        conversion_rate_dict = self._get_conversion_rate()
        company_currency_name = self.env.user.company_id.currency_id.name
        delivery_returned_list = self._get_delivery_returned(obj)

        self.env.cr.execute(sql_str)
        for row in self.env.cr.dictfetchall():
            returned_qty = sum(map(lambda d: d['returned_qty'], filter(lambda x: x['delivery_challan_no'] == row['delivery_challan_no'], delivery_returned_list)))
            row['delivered_qty'] = row['delivered_qty'] - returned_qty
            row['amount'] = row['amount'] - row['price_unit'] * returned_qty

            if row['currency_name'] != company_currency_name:
                conversion_rate = conversion_rate_dict.get(row['currency_name'], 1.0)
                amount = row['amount'] * conversion_rate
                row['amount'] = amount

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
        result_data = self._get_delivery_done(obj)

        # for displaying column dynamically
        report_for_factory = self.env.context.get('report_factory')
        delivery_report_factory = self.env.user.company_id.delivery_report_factory
        show_all_column = False if report_for_factory and delivery_report_factory else True

        # Report Utility
        ReportUtility = self.env['report.utility']

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
        sheet = workbook.add_worksheet('Delivery Report')

        # SET CELL WIDTH
        sheet.set_column(0, 0, 25)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 16)
        sheet.set_column(3, 3, 16)
        sheet.set_column(4, 4, 17)
        sheet.set_column(5, 5, 17)
        sheet.set_column(6, 6, 18)
        sheet.set_column(7, 7, 18)
        sheet.set_column(8, 8, 16)

        last_col = 8

        if show_all_column:
            sheet.set_column(9, 9, 10)
            sheet.set_column(10, 10, 10)
            sheet.set_column(11, 11, 18)
            last_col = 11

        # SHEET HEADER
        conversion_rate_dict = self._get_conversion_rate()
        sheet.merge_range(0, 0, 0, last_col, self.env.user.company_id.name, name_format)
        sheet.merge_range(1, 0, 1, last_col, self.env.user.company_id.street, address_format)
        sheet.merge_range(2, 0, 2, last_col, self.env.user.company_id.street2, address_format)
        sheet.merge_range(3, 0, 3, last_col, self.env.user.company_id.city + '-' + self.env.user.company_id.zip, address_format)
        sheet.merge_range(4, 0, 4, last_col, "Delivery Report", name_format)

        # Currency rate block
        row = 5
        if show_all_column:
            for key, val in conversion_rate_dict.items():
                if key != self.env.user.company_id.currency_id.name:
                    sheet.merge_range(row, 9, row, 11, key + ": " + str(val), bold)
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
        sheet.merge_range(row, last_col - 2, row, last_col, "Date: " + ReportUtility.get_date_from_string(obj.date_from) + " To " + ReportUtility.get_date_from_string(obj.date_to), bold)
        row += 1

        # TABLE HEADER
        row, col = row + 1, 0
        sheet.write(row, col, 'Customer Name', th_cell_center)
        sheet.write(row, col + 1, 'SO No.', th_cell_center)
        sheet.write(row, col + 2, 'SO Date', th_cell_center)
        sheet.write(row, col + 3, 'Delivery Date', th_cell_center)
        sheet.write(row, col + 4, 'Delivery Challan No.', th_cell_center)
        sheet.write(row, col + 5, 'Vat Challan No.', th_cell_center)
        sheet.write(row, col + 6, 'LC/TT/Sales Contract', th_cell_center)
        sheet.write(row, col + 7, 'Packing Mode', th_cell_center)
        sheet.write(row, col + 8, 'Delivery Qty (MT)', th_cell_center)

        if show_all_column:
            sheet.write(row, col + 9, 'Unit Price', th_cell_center)
            sheet.write(row, col + 10, 'Currency', th_cell_center)
            sheet.write(row, col + 11, 'Amount (BDT)', th_cell_center)

        # TABLE BODY
        grand_total_amount = 0.0
        row += 1
        for index, value in result_data.items():
            sheet.merge_range(row, col, row, col + last_col, value['product_name'], td_cell_left_bold)
            row += 1

            for rec in value['deliveries']:
                if rec['delivered_qty'] > 0:
                    sheet.write(row, col, rec['partner_name'], td_cell_left)
                    sheet.write(row, col + 1, rec['so_no'], td_cell_center)
                    sheet.write(row, col + 2, ReportUtility.get_date_time_from_string(rec['so_date']), td_cell_center)
                    sheet.write(row, col + 3, ReportUtility.get_date_time_from_string(rec['delivery_date']), td_cell_center)
                    sheet.write(row, col + 4, rec['delivery_challan_no'], td_cell_center)
                    sheet.write(row, col + 5, rec['vat_challan_no'], td_cell_left)
                    sheet.write(row, col + 6, rec['contract_no'], td_cell_left)
                    sheet.write(row, col + 7, rec['packing_mode'], td_cell_center)
                    sheet.write(row, col + 8, rec['delivered_qty'], no_format)

                    if show_all_column:
                        sheet.write(row, col + 9, rec['price_unit'], no_format)
                        sheet.write(row, col + 10, rec['currency_name'], td_cell_center)
                        sheet.write(row, col + 11, rec['amount'], no_format)

                    row += 1

            # SUB TOTAL
            sub_total_delivered_qty = sum(map(lambda x: x['delivered_qty'], value['deliveries']))
            sub_total_amount = sum(map(lambda x: x['amount'], filter(lambda v: v['delivered_qty'] > 0, value['deliveries'])))
            grand_total_amount += float(sub_total_amount)

            sheet.merge_range(row, col, row, col + 7, 'Sub Total', td_cell_left_bold)
            sheet.write(row, col + 8, sub_total_delivered_qty, total_format)

            if show_all_column:
                sheet.write(row, col + 9, '', total_format)
                sheet.write(row, col + 10, '', total_format)
                sheet.write(row, col + 11, sub_total_amount, total_format)

            row += 1
            # END

        # GRAND TOTAL
        if show_all_column:
            sheet.merge_range(row, col, row, col + 10, 'Grand Total', td_cell_left_bold)
            sheet.write(row, col + 11, grand_total_amount, total_format)
        # END


DeliveryReportXLSX('report.delivery_reports.delivery_report_xlsx', 'delivery.report.wizard', parser=report_sxw.rml_parse)
