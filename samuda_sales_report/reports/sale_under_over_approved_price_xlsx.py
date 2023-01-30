import datetime

from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class SaleUnderOverApprovedPriceReportXLSX(ReportXlsx):

    def _get_query_where_clause(self, obj):
        where_str = """where so.state='done' and so.operating_unit_id=%s and DATE(so.date_order) between '%s' and '%s'""" % (obj.operating_unit_id.id, obj.date_from, obj.date_to)
        #and so.partner_id=7030  and pp.product_tmpl_id=4 and sol.product_id=26'
        if obj.product_tmpl_id and not obj.product_id:
            product_ids = self.env['product.product'].search([('product_tmpl_id', '=', obj.product_tmpl_id.id), '|', ('active', '=', True), ('active', '=', False)]).ids
            if len(product_ids) > 1:
                where_str += """ AND sol.product_id IN %s""" % (tuple(product_ids),)
            else:
                where_str += """ AND sol.product_id=%s""" % product_ids[0]

        if obj.product_id:
            where_str += """ AND sol.product_id=%s""" % obj.product_id.id

        if obj.partner_id:
            where_str += """ AND so.partner_id=%s""" % obj.partner_id.id

        return where_str

    def _get_sale_products(self, obj):
        where_clause = self._get_query_where_clause(obj)
        sql_str = """select sol.product_id as product_id,sol.name as product_name, rp.name as cus_name,so.name as so_no,
                    COALESCE(sol.product_uom_qty, 0) as sold_qty,COALESCE(sol.price_unit_actual,0) as approved_price, COALESCE(sol.price_unit_max_discount, 0) as max_discount, COALESCE(sol.price_unit,0) as sale_price,rc.name as currency_name, 
                    CASE WHEN COALESCE(sol.price_unit,0) < COALESCE(sol.price_unit_actual,0)-COALESCE(sol.price_unit_max_discount,0) 
                    THEN 'Under' WHEN COALESCE(sol.price_unit,0) > COALESCE(sol.price_unit_actual,0) THEN 'Over' ELSE 'Approved' END as status 
                    from sale_order_line as sol 
                    LEFT JOIN sale_order as so ON sol.order_id = so.id
                    LEFT JOIN res_currency as rc ON rc.id = sol.currency_id
                    LEFT JOIN res_partner as rp ON rp.id = sol.order_partner_id
                    LEFT JOIN product_product as pp ON pp.id = sol.product_id
                    """+where_clause+"""
                    group by sol.product_id, sol.name, so.date_order, rp.name, so.name, sol.product_uom_qty, sol.price_unit_actual, sol.price_unit, rc.name, sol.price_unit_max_discount
                    order by so.date_order DESC
        """

        sale_over_under_dict = {}
        self.env.cr.execute(sql_str)
        for row in self.env.cr.dictfetchall():

            if row['product_id'] in sale_over_under_dict:
                sale_over_under_dict[row['product_id']]['order_lines'].append(row)
            else:
                product = self.env['product.product'].browse(row['product_id'])
                sale_over_under_dict[row['product_id']] = {}
                sale_over_under_dict[row['product_id']]['product_name'] = product.display_name
                sale_over_under_dict[row['product_id']]['order_lines'] = []
                sale_over_under_dict[row['product_id']]['order_lines'].append(row)
                sale_over_under_dict[row['product_id']]['over_count'] = 0
                sale_over_under_dict[row['product_id']]['under_count'] = 0

        return sale_over_under_dict

    def generate_xlsx_report(self, workbook, data, obj):
        result_data = self._get_sale_products(obj)

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
        td_cell_center_under = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10, 'border': 1})
        td_cell_center_under.set_font_color('#FF0000')
        td_cell_center_over = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10, 'border': 1})
        td_cell_center_over.set_font_color('#008000')
        td_cell_right = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'size': 10, 'border': 1})

        td_cell_left_bold = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})
        td_cell_center_bold = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})
        td_cell_right_bold = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})

        # WORKSHEET
        sheet = workbook.add_worksheet('Product Sold (under/over) Approved Price')

        # SET CELL WIDTH
        sheet.set_column(0, 0, 25)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 16)
        sheet.set_column(3, 3, 30)
        sheet.set_column(4, 4, 17)
        sheet.set_column(5, 5, 17)
        sheet.set_column(6, 6, 17)
        sheet.set_column(7, 6, 17)

        last_col = 7

        # SHEET HEADER
        sheet.merge_range(0, 0, 0, last_col, self.env.user.company_id.name, name_format)
        sheet.merge_range(1, 0, 1, last_col, self.env.user.company_id.street, address_format)
        sheet.merge_range(2, 0, 2, last_col, self.env.user.company_id.street2, address_format)
        sheet.merge_range(3, 0, 3, last_col, self.env.user.company_id.city + '-' + self.env.user.company_id.zip, address_format)
        sheet.merge_range(4, 0, 4, last_col, "Sales Volume Report (under/over price)", name_format)

        row = 5

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
        sheet.write(row, col + 2, 'Sold Qty (MT)', th_cell_center)
        sheet.write(row, col + 3, 'Current Approved Price (during this period)', th_cell_center)
        sheet.write(row, col + 4, 'Discount', th_cell_center)
        sheet.write(row, col + 5, 'Selling Price', th_cell_center)
        sheet.write(row, col + 6, 'Currency', th_cell_center)
        sheet.write(row, col + 7, 'Status', th_cell_center)

        # TABLE BODY
        row += 1
        col = 0
        for index, value in result_data.items():
            over = 0
            under = 0
            for rec in value['order_lines']:
                if rec['sale_price'] < (rec['approved_price'] - rec['max_discount']):
                    under += 1
                elif rec['sale_price'] > (rec['approved_price']):
                    over += 1
            sheet.merge_range(row, col, row, 2, value['product_name'], td_cell_left_bold)
            sheet.write(row, 3, " Under:" + str(under) + "/ Over:" + str(over), td_cell_center)
            sheet.merge_range(row, 4, row, last_col, "", td_cell_center)
            row += 1
            sub_total_sold_qty = 0
            for rec in value['order_lines']:
                sheet.write(row, col, rec['cus_name'], td_cell_left)
                sheet.write(row, col + 1, rec['so_no'], td_cell_left)
                sheet.write(row, col + 2, rec['sold_qty'], td_cell_right)
                sheet.write(row, col + 3, rec['approved_price'],td_cell_right)
                sheet.write(row, col + 4, rec['max_discount'], td_cell_right)
                sheet.write(row, col + 5, rec['sale_price'], td_cell_right)
                sheet.write(row, col + 6, rec['currency_name'], td_cell_center)
                td_cell_center_conditional = td_cell_center
                if rec['status'] == 'Over':
                    td_cell_center_conditional = td_cell_center_over
                elif rec['status'] == 'Under':
                    td_cell_center_conditional = td_cell_center_under
                sheet.write(row, col + 7, rec['status'], td_cell_center_conditional)
                sub_total_sold_qty += rec['sold_qty']
                row += 1
            sheet.merge_range(row, col, row, 1, 'Sub Total', td_cell_left_bold)
            sheet.merge_range(row, 2, row, last_col, sub_total_sold_qty, td_cell_left_bold)
            row += 1

SaleUnderOverApprovedPriceReportXLSX('report.samuda_sales_report.sale_under_over_approved_price_xlsx', 'sale.under.over.approved.price.report.wizard', parser=report_sxw.rml_parse)
