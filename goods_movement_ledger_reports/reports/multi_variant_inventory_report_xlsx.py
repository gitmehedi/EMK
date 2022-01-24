from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.exceptions import ValidationError, UserError
from odoo import api, fields, models, _
from datetime import date, timedelta, datetime


class MultiVariantInventoryReportXLSX(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, obj):
        ReportUtility = self.env['report.utility']
        product_report_utility = self.env['product.ledger.report.utility']
        location = self.env['stock.location'].search(
            [('operating_unit_id', '=', obj.operating_unit_id.id)])

        if not location:
            raise UserError(_("There are no stock location for this unit. "
                              "\nPlease create stock location for this unit."))

        date_from = obj.date_from
        date_start = date_from + ' 00:00:01'

        date_to = obj.date_to
        date_end = date_to + ' 23:59:59'

        location_outsource = tuple(location.ids)

        operating_unit_id = obj.operating_unit_id.id

        if obj.product_ids:
            product_ids = obj.product_ids.ids
        else:
            if self.env.user.has_group('mrp.group_mrp_user'):
                if self.env.user.has_group('mrp_gbs_access.group_mrp_adviser'):
                    product_ids = self.env['product.product'].sudo().search([]).ids
                else:
                    product_ids = self.env.user.product_ids.ids
            elif self.env.user.has_group('mrp_gbs_access.group_mrp_adviser'):
                product_ids = self.env['product.product'].sudo().search([]).ids

        date_start_obj = datetime.strptime(date_from, "%Y-%m-%d")

        date_end_obj = datetime.strptime(date_to, "%Y-%m-%d")

        report_name = 'Multi Variant Report'
        sheet = workbook.add_worksheet(report_name)
        sheet.set_column(0, 1, 16)
        # FORMAT
        bold = workbook.add_format({'bold': True, 'size': 10})
        name_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 8})
        name_border_format = workbook.add_format(
            {'align': 'center', 'border': 1, 'valign': 'vcenter', 'bold': True, 'size': 8})
        name_border_format_colored = workbook.add_format(
            {'align': 'center', 'border': 1, 'bg_color': '#eaede6', 'valign': 'vcenter', 'bold': True, 'size': 8})
        normal_format_left = workbook.add_format(
            {'align': 'left', 'size': 8})
        name_format_left = workbook.add_format({'align': 'left', 'bold': True, 'size': 8})
        header_format_left = workbook.add_format(
            {'align': 'left', 'bg_color': '#d7ecfa', 'bold': True, 'size': 8, 'border': 1})

        address_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 7})

        # SHEET HEADER
        sheet.merge_range('A1:O1', self.env.user.company_id.name, name_format)
        sheet.merge_range('A2:O2', self.env.user.company_id.street, address_format)
        sheet.merge_range('A3:O3', self.env.user.company_id.street2, address_format)
        sheet.merge_range('A4:O4', self.env.user.company_id.city + '-' + self.env.user.company_id.zip, address_format)
        sheet.merge_range('A5:O5', "Multi Variant Report", name_format)

        sheet.merge_range('A7:H7', "Operating Unit : " + obj.operating_unit_id.name, name_format_left)
        sheet.merge_range('I7:O7', "Date : " + ReportUtility.get_date_from_string(
            obj.date_from) + ' to ' + ReportUtility.get_date_from_string(obj.date_to), name_format_left)

        sheet.merge_range('A9:C9', " ", name_border_format)
        sheet.merge_range('D9:H9', "Received", name_border_format_colored)
        sheet.write(8, 8, " ", name_border_format)
        sheet.merge_range('J9:N9', "Issued", name_border_format_colored)

        sheet.write(9, 0, "Particulars", header_format_left)
        sheet.write(9, 1, "UoM", header_format_left)
        sheet.write(9, 2, "Opening Stock", header_format_left)
        sheet.write(9, 3, "Production", header_format_left)
        sheet.write(9, 4, "Purchase", header_format_left)
        sheet.write(9, 5, "By Loan", header_format_left)
        sheet.write(9, 6, "Received from Other Unit", header_format_left)
        sheet.write(9, 7, "Other Adjustment", header_format_left)
        sheet.write(9, 8, "Available Stock", header_format_left)
        sheet.write(9, 9, "Sales", header_format_left)
        sheet.write(9, 10, "Own Consumption", header_format_left)
        sheet.write(9, 11, "To Loan", header_format_left)
        sheet.write(9, 12, "Issue to Other Unit", header_format_left)
        sheet.write(9, 13, "Loss/Adjustment", header_format_left)
        sheet.write(9, 14, "Closing Stock", header_format_left)

        row_no = 10

        for product_id in product_ids:
            available_stock = 0.0
            product_obj = self.env['product.product'].browse(product_id)
            product_name = product_obj.name_get()[0][1]
            sheet.write(row_no, 0, product_name, normal_format_left)
            if product_obj.uom_id:
                sheet.write(row_no, 1, product_obj.uom_id.name, normal_format_left)
            else:
                sheet.write(row_no, 1, '', normal_format_left)

            # + ' 00:00:01'
            start_date = date_start_obj.replace(second=01).strftime("%Y-%m-%d, %H:%M:%S")
            # + ' 23:59:59'
            end_date = date_end_obj.replace(hour=23, minute=59, second=59).strftime("%Y-%m-%d, %H:%M:%S")

            if product_obj:
                product_param = "(" + str(product_obj.id) + ")"
            else:
                product_list = self.env['product.product'].search([])
                if len(product_list) == 1:
                    product_param = "(" + str(product_list.id) + ")"
                elif len(product_list) > 1:
                    product_param = str(tuple(product_list.ids))
                else:
                    product_param = '(0)'

            datewise_opening_closing_stocklist = product_report_utility.get_opening_closing_stock(start_date, end_date,
                                                                                                  location_outsource,
                                                                                                  product_param)

            if datewise_opening_closing_stocklist:
                for opening_closing_stock in datewise_opening_closing_stocklist:
                    if opening_closing_stock['opening_stock']:
                        available_stock = available_stock + float(opening_closing_stock['opening_stock'])
                        sheet.write(row_no, 2, opening_closing_stock['opening_stock'], normal_format_left)
                    else:
                        available_stock = available_stock + 0
                        sheet.write(row_no, 2, 0, normal_format_left)

                    if opening_closing_stock['closing_stock']:
                        sheet.write(row_no, 14, opening_closing_stock['closing_stock'], normal_format_left)
                    else:
                        sheet.write(row_no, 14, 0, normal_format_left)
            else:
                available_stock = available_stock + 0
                sheet.write(row_no, 2, 0, normal_format_left)
                sheet.write(row_no, 14, 0, normal_format_left)

            # datewise_production
            production_total_qty = product_report_utility.get_production_stock(start_date, end_date,
                                                                               obj.operating_unit_id.id,
                                                                               product_id)

            if production_total_qty:
                available_stock = available_stock + float(production_total_qty)
                sheet.write(row_no, 3, production_total_qty, normal_format_left)
            else:
                available_stock = available_stock + 0
                sheet.write(row_no, 3, 0, normal_format_left)
            # datewise_purchase
            datewise_purchase_stocklist = product_report_utility.get_purchase_stock(start_date, end_date,
                                                                                    obj.operating_unit_id.id,
                                                                                    product_param)

            if datewise_purchase_stocklist:
                for purchase_stock in datewise_purchase_stocklist:
                    if purchase_stock['purchase_qty']:
                        available_stock = available_stock + float(purchase_stock['purchase_qty'])
                        sheet.write(row_no, 4, purchase_stock['purchase_qty'], normal_format_left)
                    else:
                        available_stock = available_stock + 0
                        sheet.write(row_no, 4, 0, normal_format_left)
            else:
                available_stock = available_stock + 0
                sheet.write(row_no, 4, 0, normal_format_left)
            # datewise_loan_borrowed

            datewise_loan_borrowed = product_report_utility.get_loan_borrowing_stock(start_date, end_date,
                                                                                     operating_unit_id,
                                                                                     product_param)

            if datewise_loan_borrowed:
                for loan_borrowing_stock in datewise_loan_borrowed:
                    if loan_borrowing_stock['loan_borrowing_qty']:
                        available_stock = available_stock + float(loan_borrowing_stock['loan_borrowing_qty'])
                        sheet.write(row_no, 5, loan_borrowing_stock['loan_borrowing_qty'], normal_format_left)
                    else:
                        available_stock = available_stock + 0
                        sheet.write(row_no, 5, 0, normal_format_left)
            else:
                available_stock = available_stock + 0
                sheet.write(row_no, 5, 0, normal_format_left)

            # datewise_received_from_other_unit
            # datewise_other_adjustment
            datewise_other_adjustment = product_report_utility.get_other_adjustment_received(start_date, end_date,
                                                                                             operating_unit_id,
                                                                                             product_param)

            if datewise_other_adjustment:
                for other_adjustment in datewise_other_adjustment:
                    if other_adjustment['adjustment_qty']:
                        available_stock = available_stock + float(other_adjustment['adjustment_qty'])
                        sheet.write(row_no, 7, other_adjustment['adjustment_qty'], normal_format_left)
                    else:
                        available_stock = available_stock + 0
                        sheet.write(row_no, 7, 0, normal_format_left)
            else:
                available_stock = available_stock + 0
                sheet.write(row_no, 7, 0, normal_format_left)

            # datewise_available_stock
            # datewise_sales
            result_data = product_report_utility._get_delivery_done(operating_unit_id, start_date, end_date,
                                                                    product_param)
            delivery_quantity = 0
            for index, value in result_data.items():
                delivery_quantity = sum(map(lambda x: x['delivered_qty'], value['deliveries']))

            sheet.write(row_no, 9, delivery_quantity, normal_format_left)

            # datewise_own_consumption
            datewise_own_consumption_stocklist = product_report_utility.get_own_consumption_stock(start_date,
                                                                                                  end_date,
                                                                                                  operating_unit_id,
                                                                                                  product_param)

            if datewise_own_consumption_stocklist:
                for own_consumption_stock in datewise_own_consumption_stocklist:
                    if own_consumption_stock['consumed_qty']:
                        sheet.write(row_no, 10, own_consumption_stock['consumed_qty'], normal_format_left)
                    else:
                        sheet.write(row_no, 10, 0, normal_format_left)
            else:
                sheet.write(row_no, 10, 0, normal_format_left)
            # datewise_loan_lending
            datewise_loan_lending = product_report_utility.get_loan_lending_stock(start_date, end_date,
                                                                                  operating_unit_id,
                                                                                  product_param)

            if datewise_loan_lending:
                for loan_lending_stock in datewise_loan_lending:
                    if loan_lending_stock['loan_lending_qty']:
                        sheet.write(row_no, 11, loan_lending_stock['loan_lending_qty'], normal_format_left)
                    else:
                        sheet.write(row_no, 11, 0, normal_format_left)
            else:
                sheet.write(row_no, 11, 0, normal_format_left)

            # datewise_issue_to_other_unit
            # datewise_loss_adjustment
            datewise_loss_adjustment = product_report_utility.get_loss_adjustment_issued(start_date, end_date,
                                                                                         operating_unit_id,
                                                                                         product_param)

            if datewise_loss_adjustment:
                for loss_adjustment in datewise_loss_adjustment:
                    if loss_adjustment['adjustment_qty']:
                        sheet.write(row_no, 13, loss_adjustment['adjustment_qty'], normal_format_left)
                    else:
                        sheet.write(row_no, 13, 0, normal_format_left)
            else:
                sheet.write(row_no, 13, 0, normal_format_left)

            sheet.write(row_no, 8, available_stock, normal_format_left)
            row_no = row_no + 1
        data['name'] = 'Multi Variant Report'


MultiVariantInventoryReportXLSX('report.goods_movement_ledger_reports.multi_variant_inventory_report_xlsx',
                                'multi.variant.inventory.report.wizard', parser=report_sxw.rml_parse)
