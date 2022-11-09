import datetime
from datetime import datetime, timedelta
from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class SecondAcceptanceInfoXLSX(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, obj):
        data = {}
        product = []
        sl = 0
        for ou in obj.product_temp_id:
            product.append(ou.name)
        data['product_temp_id'] = tuple(obj.product_temp_id.ids)
        data['product_temp_name'] = product

        state_condition = 'to_seller_bank', 'to_buyer_bank', 'to_bill_id'
        result_data = self.env['acceptance.report.utility'].get_report_data(data, state_condition)
        current_date_time = datetime.now() + timedelta(hours=6)
        current_date_time = current_date_time.strftime('%Y-%m-%d %H:%M:%S')

        # Report Utility
        ReportUtility = self.env['report.utility']

        bold = workbook.add_format({'bold': True, 'size': 10})
        total_format = workbook.add_format({'num_format': '#,###0.00', 'bold': True, 'size': 10, 'border': 1})

        name_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 12})
        address_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10})

        # table header cell format
        th_cell_center = workbook.add_format(
            {'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})

        # table body cell format
        td_cell_left = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'size': 10, 'border': 1})
        td_cell_center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10, 'border': 1})
        td_cell_left_bold = workbook.add_format(
            {'align': 'left', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})

        # WORKSHEET
        sheet = workbook.add_worksheet('Second Acceptance Report')

        # SET CELL WIDTH
        sheet.set_column(0, 0, 10)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 16)
        sheet.set_column(3, 3, 16)
        sheet.set_column(4, 4, 17)
        sheet.set_column(5, 5, 17)
        sheet.set_column(6, 6, 18)
        sheet.set_column(7, 7, 18)
        sheet.set_column(8, 8, 16)
        sheet.set_column(9, 9, 16)
        sheet.set_column(10, 10, 16)
        sheet.set_column(11, 11, 16)
        sheet.set_column(12, 12, 16)
        sheet.set_column(13, 13, 16)
        sheet.set_column(14, 14, 16)
        sheet.set_column(15, 14, 16)

        last_col = 15

        # SHEET HEADER
        sheet.merge_range(0, 0, 0, last_col, self.env.user.company_id.name, name_format)
        sheet.merge_range(1, 0, 1, last_col, self.env.user.company_id.street, address_format)
        sheet.merge_range(2, 0, 2, last_col, self.env.user.company_id.street2, address_format)
        sheet.merge_range(3, 0, 3, last_col, self.env.user.company_id.city + '-' + self.env.user.company_id.zip,
                          address_format)
        sheet.merge_range(4, 0, 4, last_col, "Second Acceptance Report", name_format)

        row = 6
        # Filter Block
        product_name = ''
        for product in data['product_temp_name']:
            if product:
                product_name += product + ', '
                new_product_name = ''.join(product_name.rsplit(',', 1))
                sheet.merge_range(row, 0, row, 2, "Product Name: " + new_product_name, bold)

        sheet.merge_range(6, 11, 6, 14, "Reported On: " + ReportUtility.get_date_time_from_string(current_date_time),
                          bold)
        row += 1

        # TABLE HEADER
        row, col = row + 1, 0
        sheet.write(row, col, 'SL', th_cell_center)
        sheet.write(row, col + 1, 'Customer', th_cell_center)
        sheet.write(row, col + 2, 'L/C No.', th_cell_center)
        sheet.write(row, col + 3, 'Shipment No', th_cell_center)
        sheet.write(row, col + 4, 'Value', th_cell_center)
        sheet.write(row, col + 5, 'Tenor.', th_cell_center)
        sheet.write(row, col + 6, 'TBL Receive on', th_cell_center)
        sheet.write(row, col + 7, 'Party Bank Receive', th_cell_center)
        sheet.write(row, col + 8, 'Aging', th_cell_center)
        sheet.write(row, col + 9, 'First Delivery', th_cell_center)
        sheet.write(row, col + 10, 'Last Delivery', th_cell_center)
        sheet.write(row, col + 11, 'Bill ID', th_cell_center)
        sheet.write(row, col + 12, 'Remarks/Status', th_cell_center)
        sheet.write(row, col + 13, 'F.P.R', th_cell_center)
        sheet.write(row, col + 14, 'Bank', th_cell_center)
        sheet.write(row, col + 15, 'Branch', th_cell_center)
        row += 1

        # TABLE BODY
        for product_data in result_data['acceptances']:
            for rec in result_data['acceptances'][product_data]:
                if len(rec)>0:
                    sheet.merge_range(row, col, row, col + last_col, product_data, td_cell_left_bold)
            row += 1

            for rec in result_data['acceptances'][product_data]:
                if rec:
                    sl = sl + 1
                    sheet.write(row, col, sl, td_cell_left)
                    sheet.write(row, col + 1, rec['customer'], td_cell_left)
                    sheet.write(row, col + 2, rec['lc_name'], td_cell_center)
                    sheet.write(row, col + 3, rec['shipment_name'], td_cell_center)
                    sheet.write(row, col + 4, rec['value'], td_cell_center)
                    sheet.write(row, col + 5, rec['tenor'], td_cell_center)
                    sheet.write(row, col + 6, ReportUtility.get_date_from_string(rec['seller_bank_date']),
                                td_cell_center)
                    sheet.write(row, col + 7, ReportUtility.get_date_from_string(rec['buyer_bank_date']),
                                td_cell_center)
                    sheet.write(row, col + 8, rec['aging'], td_cell_center)
                    sheet.write(row, col + 9, ReportUtility.get_date_time_from_string(rec['first_delivery_date']),
                                td_cell_center)
                    sheet.write(row, col + 10, ReportUtility.get_date_time_from_string(rec['last_delivery_date']),
                                td_cell_center)
                    sheet.write(row, col + 11, rec['bill_id'], td_cell_center)
                    sheet.write(row, col + 12, rec['comment'], td_cell_center)
                    sheet.write(row, col + 13, rec['sale_persons'], td_cell_center)
                    sheet.write(row, col + 14, rec['bank_code'], td_cell_center)
                    sheet.write(row, col + 15, rec['bank_branch'], td_cell_center)

                    row += 1

            # SUB TOTAL
            for rec in result_data['total'][product_data]:
                for recd in result_data['acceptances'][product_data]:
                    if len(recd) > 0:
                        sheet.merge_range(row, col, row, col + 3, 'Sub Total', td_cell_left_bold)
                        sheet.write(row, col + 4, rec['total_val'], total_format)
                        sheet.write(row, col + 5, '', total_format)
                        sheet.write(row, col + 6, '', total_format)
                        sheet.write(row, col + 7, '', total_format)
                        sheet.write(row, col + 8, '', total_format)
                        sheet.write(row, col + 9, '', total_format)
                        sheet.write(row, col + 10, '', total_format)
                        sheet.write(row, col + 11, '', total_format)
                        sheet.write(row, col + 12, '', total_format)
                        sheet.write(row, col + 13, '', total_format)
                        sheet.write(row, col + 14, '', total_format)
                        sheet.write(row, col + 15, '', total_format)

                        row += 1

                        break

SecondAcceptanceInfoXLSX('report.lc_sales_local_report.lc_second_acceptance_report_xlsx',
                         'local.second.acceptance.wizard', parser=report_sxw.rml_parse)