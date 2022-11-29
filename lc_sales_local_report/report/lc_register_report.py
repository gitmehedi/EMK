from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from datetime import datetime


def date_subtract_date_to_days(date1, date2):
    days = 0
    if date1 and date2:
        d1 = datetime.strptime(date1, "%d-%m-%Y")
        d2 = datetime.strptime(date2, "%d-%m-%Y")
        days = (d1 - d2).days
    return days


class LcRegisterXLSX(ReportXlsx):

    def get_amount_in_bdt(self, amount, currency):
        if amount == '':
            amount = 0
        if currency == 'BDT':
            return amount
        else:
            res_currency = self.env['res.currency'].search([('name', '=', currency)])
            if res_currency and amount:
                reverse_rate = res_currency.reverse_rate
                return float(amount) * reverse_rate
            else:
                return amount

    @staticmethod
    def get_sheet_table_head(sheet, workbook):
        header_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bold': True, 'size': 8, 'border': 1,
             'text_wrap': True})
        header_format_left.set_font_name('Times New Roman')

        sheet.write(7, 0, "SL", header_format_left)
        sheet.write(7, 1, "Party Name", header_format_left)
        sheet.write(7, 2, "Executive Name", header_format_left)
        sheet.write(7, 3, "Product Name", header_format_left)
        sheet.write(7, 4, "PI No", header_format_left)
        sheet.write(7, 5, "SO NO", header_format_left)
        sheet.write(7, 6, "LC No", header_format_left)
        sheet.write(7, 7, "LC Date", header_format_left)
        sheet.write(7, 8, "LC Quantity", header_format_left)
        sheet.write(7, 9, "LC Amount", header_format_left)
        sheet.write(7, 10, "Currency", header_format_left)
        sheet.write(7, 11, "Delivery Quantity", header_format_left)
        sheet.write(7, 12, "Shipment No", header_format_left)
        sheet.write(7, 13, "Shipment Qty", header_format_left)
        sheet.write(7, 14, "Shipment Amt", header_format_left)
        sheet.write(7, 15, "Shipment Amt in BDT", header_format_left)
        sheet.write(7, 16, "Undelivered Quantity", header_format_left)
        sheet.write(7, 17, "Tenure", header_format_left)
        sheet.write(7, 18, "Shipment Date", header_format_left)
        sheet.write(7, 19, "Expiry date", header_format_left)
        sheet.write(7, 20, "Last Delivery date/Date of Transfer", header_format_left)
        sheet.write(7, 21, "Delivery Details", header_format_left)
        sheet.write(7, 22, "Doc. Preparation Date", header_format_left)
        sheet.write(7, 23, "Aging (Days) Document Prepared", header_format_left)
        sheet.write(7, 24, "Doc. submit to Party Date/1st Acceptance", header_format_left)
        sheet.write(7, 25, "First Acceptance Doc. Collection  Date", header_format_left)
        sheet.write(7, 26, "Aging (Days) First Acceptance", header_format_left)
        sheet.write(7, 27, "Percentage of 1st Acceptance in a period or month", header_format_left)
        sheet.write(7, 28, "Seller Bank Receive", header_format_left)
        sheet.write(7, 29, "To Buyer Bank", header_format_left)
        sheet.write(7, 30, "Aging (Days) 2nd Acceptance", header_format_left)
        sheet.write(7, 31, "Maturity Date", header_format_left)
        sheet.write(7, 32, "Shipment Done Date", header_format_left)
        sheet.write(7, 33, "Discrepancy Amount", header_format_left)
        sheet.write(7, 34, "AIT Amount", header_format_left)
        sheet.write(7, 35, "Payment Rec. Date", header_format_left)
        sheet.write(7, 36, "Payment Rec. Amount", header_format_left)
        sheet.write(7, 37, "Payment Rec. Amount in BDT", header_format_left)
        sheet.write(7, 38, "Payment Charge", header_format_left)
        sheet.write(7, 39, "Discrepancy Details", header_format_left)
        sheet.write(7, 40, "Aging /(Days) Final Payment", header_format_left)
        sheet.write(7, 41, "Party Bank & Branch", header_format_left)
        sheet.write(7, 42, "Samuda Bank Name", header_format_left)
        sheet.write(7, 43, "Packing Type", header_format_left)
        sheet.write(7, 44, "Bill ID NO", header_format_left)

    def set_sheet_table_data(self, obj, sheet, workbook, datas):
        ReportUtility = self.env['report.utility']
        name_format_left_int = workbook.add_format(
            {'align': 'left', 'border': 1, 'bold': False, 'size': 8, 'text_wrap': True})
        name_border_format_colored = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'border': 1, 'valign': 'vcenter', 'bold': False, 'size': 8,
             'text_wrap': True})
        name_border_format_colored.set_font_name('Times New Roman')
        name_border_format_colored_text_right = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'right', 'border': 1, 'valign': 'vcenter', 'bold': False, 'size': 8,
             'text_wrap': True})
        name_border_format_colored_text_right.set_font_name('Times New Roman')
        name_border_format_colored_bold = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'right', 'border': 1, 'valign': 'vcenter', 'bold': True, 'size': 8,
             'text_wrap': True})
        name_border_format_colored_bold.set_font_name('Times New Roman')

        footer_lc_quantity = 0.0
        footer_lc_amount = 0.0
        footer_lc_delivery_qty = 0.0
        footer_shipment_qty = 0.0
        footer_shipment_amount = 0.0
        footer_shipment_amount_in_bdt = 0.0
        footer_undelivery_qty = 0.0
        footer_aging_days = 0.0
        footer_aging_2nd_acceptance_days = 0.0
        footer_discrepancy_amount = 0.0
        footer_ait_amount = 0.0
        footer_payment_charge = 0.0
        footer_payment_rec_amount = 0.0
        footer_payment_rec_amount_in_bdt = 0.0
        sl = 0
        percent_number_of_row = 0
        row = 7
        condition_above_row = 0
        lc_list = []
        for data in datas:
            export_excel = True
            lc_id = data['lc_id'] if 'lc_id' in data else ''
            delivered_qty = self.get_delivered_qty(lc_id)
            if delivered_qty == 0.0 and str(obj.filter_by) == "goods_delivered_doc_not_prepared":
                export_excel = False

            if export_excel:
                document_qty = self.get_document_qty(lc_id)

                un_shipment_qty = float(delivered_qty) - float(document_qty)

                shipment_id = data['shipment_id'] if 'shipment_id' in data else ''
                so_name = data['so_name'] if 'so_name' in data else ''
                delivery_details_date_of_trans = self.get_delivery_detail(lc_id, shipment_id, so_name)
                # lc_qty = self.get_lc_qty(lc_id)
                lc_qty = data['product_qty'] if 'product_qty' in data else '0'
                region_type = data['region_type'] if 'region_type' in data else ''

                if lc_qty:
                    undelivered_qty = lc_qty - delivered_qty
                else:
                    undelivered_qty = 0


                sl = sl + 1
                row = row + 1
                sheet.write(row, 0, sl, name_format_left_int)
                sheet.write(row, 1, data['party_name'], name_border_format_colored)
                sheet.write(row, 2, data['executive_name'], name_border_format_colored)
                sheet.write(row, 3, data['product_name'], name_border_format_colored)
                sheet.write(row, 4, self.get_lc_pi_no(lc_id) if lc_id != '' else data['pi_name'],
                            name_border_format_colored)
                sheet.write(row, 5, self.get_lc_so_no(lc_id) if lc_id != '' else data['so_name'],
                            name_border_format_colored)
                sheet.write(row, 6, data['lc_number'] if 'lc_number' in data else '', name_border_format_colored)
                sheet.write(row, 7, ReportUtility.get_date_from_string(data['lc_date']) if 'lc_date' in data else '',
                            name_border_format_colored_text_right)
                sheet.write(row, 8, lc_qty, name_border_format_colored_text_right)
                footer_lc_quantity += float(lc_qty)
                sheet.write(row, 9, data['lc_amount'] if 'lc_amount' in data else '0', name_border_format_colored_text_right)
                footer_lc_amount += float(data['lc_amount'] if 'lc_amount' in data else 0)
                sheet.write(row, 10, data['currency'] if 'currency' in data else '', name_border_format_colored)
                sheet.write(row, 11, str(delivered_qty) if lc_id != '' else data['qty_delivery'], name_border_format_colored_text_right)
                if lc_id == '':
                    delivered_qty = float(data['qty_delivery'])
                footer_lc_delivery_qty += delivered_qty

                sheet.write(row, 12, data['shipment_no'] if 'shipment_no' in data else '', name_border_format_colored)
                sheet.write(row, 13, data['shipment_qty'] if 'shipment_qty' in data else '0',
                            name_border_format_colored_text_right)
                footer_shipment_qty += float(data['shipment_qty'] if 'shipment_qty' in data else 0)
                sheet.write(row, 14, data['shipment_amount'] if 'shipment_amount' in data else '0',
                            name_border_format_colored_text_right)
                footer_shipment_amount = float(data['shipment_amount'] if 'shipment_amount' in data else 0)
                shipment_amount_in_bdt = self.get_amount_in_bdt(
                    data['shipment_amount'] if 'shipment_amount' in data else '',
                    data['currency'] if 'currency' in data else '')
                sheet.write(row, 15, shipment_amount_in_bdt, name_border_format_colored_text_right)
                footer_shipment_amount_in_bdt += float(shipment_amount_in_bdt if shipment_amount_in_bdt is not None else 0)
                sheet.write(row, 16, str(undelivered_qty) if lc_id != '' else data['undelivered_qty'], name_border_format_colored_text_right)
                if lc_id == '':
                    undelivered_qty = data['undelivered_qty']
                footer_undelivery_qty += float(undelivered_qty)

                sheet.write(row, 17, data['tenure'] if 'tenure' in data else '', name_border_format_colored)
                sheet.write(row, 18,
                            ReportUtility.get_date_from_string(data['shipment_date']) if 'shipment_date' in data else '',
                            name_border_format_colored_text_right)
                sheet.write(row, 19,
                            ReportUtility.get_date_from_string(data['expiry_date']) if 'expiry_date' in data else '',
                            name_border_format_colored_text_right)
                sheet.write(row, 20, delivery_details_date_of_trans[1], name_border_format_colored)
                sheet.write(row, 21, delivery_details_date_of_trans[0], name_border_format_colored)
                sheet.write(row, 22, ReportUtility.get_date_from_string(
                    data['doc_preparation_date']) if 'doc_preparation_date' in data else '',
                            name_border_format_colored_text_right)
                if 'doc_preparation_date' in data:
                    sheet.write(row, 23,
                                date_subtract_date_to_days(ReportUtility.get_date_from_string(data['doc_preparation_date']),
                                                           delivery_details_date_of_trans[1]),
                                name_border_format_colored_text_right)
                else:
                    sheet.write(row, 23, '', name_border_format_colored_text_right)

                if region_type == 'local':
                    sheet.write(row, 24, ReportUtility.get_date_from_string(
                        data['doc_dispatch_to_party_date']) if 'doc_dispatch_to_party_date' in data else '',
                                name_border_format_colored_text_right)
                elif region_type == 'foreign':
                    sheet.write(row, 24, ReportUtility.get_date_from_string(
                        data['doc_dispatch_to_party_date_foreign']) if 'doc_dispatch_to_party_date_foreign' in data else '',
                                name_border_format_colored_text_right)

                sheet.write(row, 25, ReportUtility.get_date_from_string(
                    data['first_acceptance_doc_submission_date']) if 'first_acceptance_doc_submission_date' in data else '',
                            name_border_format_colored_text_right)

                if region_type == 'local':
                    aging_days = data['aging_first_acceptance_days'] if 'aging_first_acceptance_days' in data else '0'
                    if aging_days is None:
                        aging_days = 0
                    sheet.write(row, 26, aging_days, name_border_format_colored_text_right)
                    footer_aging_days += float(aging_days)
                elif region_type == 'foreign':
                    aging_days = data['aging_first_acceptance_days_foreign'] if 'aging_first_acceptance_days_foreign' in data else '0'
                    if aging_days is None:
                        aging_days = 0
                    sheet.write(row, 26, aging_days, name_border_format_colored_text_right)

                percentage_of_first_acceptance_days = data['percentage_of_first_acceptance'] if 'percentage_of_first_acceptance' in data else '0'
                sheet.write(row, 27, percentage_of_first_acceptance_days, name_border_format_colored_text_right)
                if percentage_of_first_acceptance_days > 0:
                    percent_number_of_row += 1
                if str(obj.filter_by) == "percentage_of_first_acceptance_collection":
                    if int(percentage_of_first_acceptance_days) > int(obj.acceptance_default_value):
                        condition_above_row += 1

                sheet.write(row, 28, ReportUtility.get_date_from_string(
                        data['to_seller_bank_date']) if 'to_seller_bank_date' in data else '',
                                name_border_format_colored_text_right)

                if region_type == 'local':
                    sheet.write(row, 29, ReportUtility.get_date_from_string(
                        data['to_buyer_bank_date']) if 'to_buyer_bank_date' in data else '',
                                name_border_format_colored_text_right)
                elif region_type == 'foreign':
                    sheet.write(row, 29, ReportUtility.get_date_from_string(
                        data['to_buyer_bank_date_foreign']) if 'to_buyer_bank_date_foreign' in data else '',
                                name_border_format_colored_text_right)

                if region_type == 'local':
                    sheet.write(row, 30, data['aging_2nd_acceptance_days'] if 'aging_2nd_acceptance_days' in data else '0',
                                name_border_format_colored_text_right)
                    footer_aging_2nd_acceptance_days += data[
                        'aging_2nd_acceptance_days'] if 'aging_2nd_acceptance_days' in data else 0
                elif region_type == 'foreign':
                    sheet.write(row, 30, 'N/A', name_border_format_colored)

                sheet.write(row, 31,
                            ReportUtility.get_date_from_string(data['maturity_date']) if 'maturity_date' in data else '',
                            name_border_format_colored_text_right)
                sheet.write(row, 32, ReportUtility.get_date_from_string(
                    data['shipment_done_date']) if 'shipment_done_date' in data else '',
                            name_border_format_colored_text_right)
                sheet.write(row, 33, data['discrepancy_amount'] if 'discrepancy_amount' in data else '0',
                            name_border_format_colored_text_right)
                footer_discrepancy_amount += float(data['discrepancy_amount'] if 'discrepancy_amount' in data else 0)
                if region_type == 'local':
                    sheet.write(row, 34, data['ait_amount'] if 'ait_amount' in data else '0',
                                name_border_format_colored_text_right)
                    footer_ait_amount += float(data['ait_amount'] if 'ait_amount' in data else 0)
                elif region_type == 'foreign':
                    sheet.write(row, 34, 'N/A', name_border_format_colored)

                sheet.write(row, 35, ReportUtility.get_date_from_string(
                    data['payment_rec_date']) if 'payment_rec_date' in data else '', name_border_format_colored_text_right)
                sheet.write(row, 36, data['payment_rec_amount'] if 'payment_rec_amount' in data else '0',
                            name_border_format_colored_text_right)
                payment_rec_amount_in_bdt = self.get_amount_in_bdt(
                    data['payment_rec_amount'] if 'shipment_amount' in data else '',
                    data['currency'] if 'currency' in data else '')
                sheet.write(row, 37, payment_rec_amount_in_bdt,
                            name_border_format_colored_text_right)
                footer_payment_rec_amount += float(data['payment_rec_amount'] if 'payment_rec_amount' in data else 0)
                footer_payment_rec_amount_in_bdt += payment_rec_amount_in_bdt
                sheet.write(row, 38, data['payment_charge'] if 'payment_charge' in data else '0',
                            name_border_format_colored_text_right)
                footer_payment_charge += float(data['payment_charge'] if 'payment_charge' in data else 0)
                sheet.write(row, 39, data['comment'] if 'comment' in data else '', name_border_format_colored)
                sheet.write(row, 40, date_subtract_date_to_days(
                    ReportUtility.get_date_from_string(data['shipment_done_date']) if 'shipment_done_date' in data else '',
                    ReportUtility.get_date_from_string(data['maturity_date']) if 'maturity_date' in data else ''),
                            name_border_format_colored_text_right)
                sheet.write(row, 41, data['second_party_bank'] if 'second_party_bank' in data else '',
                            name_border_format_colored)
                sheet.write(row, 42, data['samuda_bank_name'] if 'samuda_bank_name' in data else '',
                            name_border_format_colored)
                sheet.write(row, 43, data['packing_type'] if 'packing_type' in data else '', name_border_format_colored)
                sheet.write(row, 44, data['bill_id_no'] if 'bill_id_no' in data else '', name_border_format_colored)


                #shipment not create line
                if un_shipment_qty > 0 and delivered_qty > 0 and data['lc_number'] not in lc_list and str(obj.filter_by) == 'goods_delivered_doc_not_prepared':
                    lc_list.append(data['lc_number'])

                    sl = sl + 1
                    row = row + 1

                    sheet.write(row, 0, sl, name_format_left_int)
                    sheet.write(row, 1, data['party_name'], name_border_format_colored)
                    sheet.write(row, 2, data['executive_name'], name_border_format_colored)
                    sheet.write(row, 3, data['product_name'], name_border_format_colored)
                    sheet.write(row, 4, self.get_lc_pi_no(lc_id) if lc_id != '' else data['pi_name'],
                                name_border_format_colored)
                    sheet.write(row, 5, self.get_lc_so_no(lc_id) if lc_id != '' else data['so_name'],
                                name_border_format_colored)
                    sheet.write(row, 6, data['lc_number'] if 'lc_number' in data else '', name_border_format_colored)
                    sheet.write(row, 7, ReportUtility.get_date_from_string(data['lc_date']) if 'lc_date' in data else '',
                                name_border_format_colored_text_right)
                    sheet.write(row, 8, lc_qty, name_border_format_colored_text_right)
                    footer_lc_quantity += float(lc_qty)
                    sheet.write(row, 9, data['lc_amount'] if 'lc_amount' in data else '',
                                name_border_format_colored_text_right)
                    footer_lc_amount += float(data['lc_amount'] if 'lc_amount' in data else 0)
                    sheet.write(row, 10, data['currency'] if 'currency' in data else '', name_border_format_colored)
                    sheet.write(row, 11, str(delivered_qty), name_border_format_colored_text_right)
                    footer_lc_delivery_qty += delivered_qty
                    sheet.write(row, 12, 'No Shipment Created', name_border_format_colored)
                    sheet.write(row, 13, un_shipment_qty, name_border_format_colored_text_right)
                    sheet.write(row, 14, '0', name_border_format_colored_text_right)
                    shipment_amount_in_bdt = self.get_amount_in_bdt(data['shipment_amount'] if 'shipment_amount' in data else '0', data['currency'] if 'currency' in data else '')
                    sheet.write(row, 15, shipment_amount_in_bdt, name_border_format_colored_text_right)
                    footer_shipment_amount_in_bdt += float(shipment_amount_in_bdt if shipment_amount_in_bdt is not None else 0)
                    sheet.write(row, 16, '0', name_border_format_colored_text_right)
                    sheet.write(row, 17, data['tenure'] if 'tenure' in data else '', name_border_format_colored)
                    sheet.write(row, 18, ReportUtility.get_date_from_string(
                        data['shipment_date']) if 'shipment_date' in data else '', name_border_format_colored_text_right)
                    sheet.write(row, 19, ReportUtility.get_date_from_string(data['expiry_date']) if 'expiry_date' in data else '',
                                name_border_format_colored_text_right)
                    sheet.write(row, 20, delivery_details_date_of_trans[1], name_border_format_colored)
                    sheet.write(row, 21, delivery_details_date_of_trans[0], name_border_format_colored)
                    sheet.write(row, 22, ReportUtility.get_date_from_string(data['doc_preparation_date']) if 'doc_preparation_date' in data else '',
                                name_border_format_colored_text_right)
                    if 'doc_preparation_date' in data:
                        sheet.write(row, 23, date_subtract_date_to_days(
                            ReportUtility.get_date_from_string(data['doc_preparation_date']),
                            delivery_details_date_of_trans[1]), name_border_format_colored_text_right)
                    else:
                        sheet.write(row, 23, '', name_border_format_colored_text_right)

                    if region_type == 'local':
                        sheet.write(row, 24, ReportUtility.get_date_from_string(
                            data['doc_dispatch_to_party_date']) if 'doc_dispatch_to_party_date' in data else '',
                                    name_border_format_colored_text_right)
                    elif region_type == 'foreign':
                        sheet.write(row, 24, ReportUtility.get_date_from_string(data['doc_dispatch_to_party_date_foreign']) if 'doc_dispatch_to_party_date_foreign' in data else '',
                                    name_border_format_colored_text_right)

                    sheet.write(row, 25, ReportUtility.get_date_from_string(data['first_acceptance_doc_submission_date']) if 'first_acceptance_doc_submission_date' in data else '',
                                name_border_format_colored_text_right)

                    if region_type == 'local':
                        aging_days = 0
                        sheet.write(row, 26, aging_days, name_border_format_colored_text_right)
                    elif region_type == 'foreign':
                        aging_days = 0
                        sheet.write(row, 26, aging_days, name_border_format_colored_text_right)

                    sheet.write(row, 27, '', name_border_format_colored_text_right)

                    sheet.write(row, 28, ReportUtility.get_date_from_string(
                            data['to_seller_bank_date']) if 'to_seller_bank_date' in data else '',
                                    name_border_format_colored_text_right)

                    if region_type == 'local':
                        sheet.write(row, 29, ReportUtility.get_date_from_string(
                            data['to_buyer_bank_date']) if 'to_buyer_bank_date' in data else '',
                                    name_border_format_colored_text_right)
                    elif region_type == 'foreign':
                        sheet.write(row, 29, ReportUtility.get_date_from_string(
                            data['to_buyer_bank_date_foreign']) if 'to_buyer_bank_date_foreign' in data else '',
                                    name_border_format_colored_text_right)

                    if region_type == 'local':
                        sheet.write(row, 30,data['aging_2nd_acceptance_days'] if 'aging_2nd_acceptance_days' in data else '0',
                                    name_border_format_colored_text_right)
                        footer_aging_2nd_acceptance_days += data['aging_2nd_acceptance_days'] if 'aging_2nd_acceptance_days' in data else 0
                    elif region_type == 'foreign':
                        sheet.write(row, 30, 'N/A', name_border_format_colored)

                    sheet.write(row, 31, ReportUtility.get_date_from_string(
                        data['maturity_date']) if 'maturity_date' in data else '',
                                name_border_format_colored_text_right)
                    sheet.write(row, 32, ReportUtility.get_date_from_string(
                        data['shipment_done_date']) if 'shipment_done_date' in data else '',
                                name_border_format_colored_text_right)
                    sheet.write(row, 33, data['discrepancy_amount'] if 'discrepancy_amount' in data else '0',
                                name_border_format_colored_text_right)
                    footer_discrepancy_amount += float(data['discrepancy_amount'] if 'discrepancy_amount' in data else 0)
                    if region_type == 'local':
                        sheet.write(row, 34, data['ait_amount'] if 'ait_amount' in data else '0',
                                    name_border_format_colored_text_right)
                        footer_ait_amount += float(data['ait_amount'] if 'ait_amount' in data else 0)
                    elif region_type == 'foreign':
                        sheet.write(row, 34, 'N/A', name_border_format_colored)

                    sheet.write(row, 35, ReportUtility.get_date_from_string(data['payment_rec_date']) if 'payment_rec_date' in data else '',
                                name_border_format_colored_text_right)
                    sheet.write(row, 36, data['payment_rec_amount'] if 'payment_rec_amount' in data else '0',
                                name_border_format_colored_text_right)
                    payment_rec_amount_in_bdt = self.get_amount_in_bdt(
                        data['payment_rec_amount'] if 'shipment_amount' in data else '',
                        data['currency'] if 'currency' in data else '')
                    sheet.write(row, 37, payment_rec_amount_in_bdt,
                                name_border_format_colored_text_right)
                    footer_payment_rec_amount += float(data['payment_rec_amount'] if 'payment_rec_amount' in data else 0)
                    footer_payment_rec_amount_in_bdt += payment_rec_amount_in_bdt
                    sheet.write(row, 38, data['payment_charge'] if 'payment_charge' in data else '0',
                                name_border_format_colored_text_right)
                    footer_payment_charge += float(data['payment_charge'] if 'payment_charge' in data else 0)
                    sheet.write(row, 39, data['comment'] if 'comment' in data else '', name_border_format_colored)
                    sheet.write(row, 40, date_subtract_date_to_days(ReportUtility.get_date_from_string(
                        data['shipment_done_date']) if 'shipment_done_date' in data else '',
                                                                    ReportUtility.get_date_from_string(data[
                                                                                                           'maturity_date']) if 'maturity_date' in data else ''),
                                name_border_format_colored_text_right)
                    sheet.write(row, 41, data['second_party_bank'] if 'second_party_bank' in data else '',
                                name_border_format_colored)
                    sheet.write(row, 42, data['samuda_bank_name'] if 'samuda_bank_name' in data else '',
                                name_border_format_colored)
                    sheet.write(row, 43, data['packing_type'] if 'packing_type' in data else '', name_border_format_colored)
                    sheet.write(row, 44, data['bill_id_no'] if 'bill_id_no' in data else '', name_border_format_colored)

        # footer
        row += 1
        for n in range(0, 44):
            if n in (0, 8, 9, 11, 13, 14, 15, 16, 26, 27, 30, 33, 34, 36, 37, 38):
                if n == 0:
                    sheet.write(row, n, 'Total ', name_border_format_colored_bold)
                if n == 8:
                    sheet.write(row, n, footer_lc_quantity, name_border_format_colored_bold)
                if n == 9:
                    sheet.write(row, n, footer_lc_amount, name_border_format_colored_bold)
                if n == 11:
                    sheet.write(row, n, footer_lc_delivery_qty, name_border_format_colored_bold)
                if n == 13:
                    sheet.write(row, 13, footer_shipment_qty, name_border_format_colored_bold)
                if n == 14:
                    sheet.write(row, 14, footer_shipment_amount, name_border_format_colored_bold)
                if n == 15:
                    sheet.write(row, 15, footer_shipment_amount_in_bdt, name_border_format_colored_bold)
                if n == 16:
                    sheet.write(row, 16, footer_undelivery_qty, name_border_format_colored_bold)
                if n == 26:
                    sheet.write(row, 26, footer_aging_days, name_border_format_colored_bold)
                if n == 27:
                    if str(obj.filter_by) == "percentage_of_first_acceptance_collection" and condition_above_row > 0:
                        footer_percentage = (float(condition_above_row) / float(percent_number_of_row)) * 100
                        sheet.write(row, 27, str(round(footer_percentage,2)) + "%", name_border_format_colored_bold)
                    else:
                        sheet.write(row, 27, '0.00', name_border_format_colored_bold)

                if n == 30:
                    sheet.write(row, 30, footer_aging_2nd_acceptance_days, name_border_format_colored_bold)

                if n == 33:
                    sheet.write(row, 33, footer_discrepancy_amount, name_border_format_colored_bold)
                if n == 34:
                    sheet.write(row, 34, footer_ait_amount, name_border_format_colored_bold)
                if n == 36:
                    sheet.write(row, 36, footer_payment_rec_amount, name_border_format_colored_bold)
                if n == 37:
                    sheet.write(row, 37, footer_payment_rec_amount_in_bdt, name_border_format_colored_bold)
                if n == 38:
                    sheet.write(row, 38, footer_payment_charge, name_border_format_colored_bold)
            else:
                sheet.write(row, n, '', name_border_format_colored_bold)

    def get_delivery_detail(self, lc_id, shipment_id, so_name):

        if shipment_id:
            query = """select * from lc_shipment_invoice_rel where shipment_id = %s""" % shipment_id
            self.env.cr.execute(query)
            purchase_shipment_invoices = self.env.cr.dictfetchall()

            if purchase_shipment_invoices:
                purchase_shipment_inv = ''
                for ship_inv in purchase_shipment_invoices:
                    purchase_shipment_inv += str(ship_inv['invoice_id']) + ','
                purchase_shipment_inv = purchase_shipment_inv[:-1]
                query = """
                        select distinct sp.name as name, sp.min_date as min_date, sp.date_done as date_done, spo.qty_done as qty_delivered
                        from stock_picking as sp
                        LEFT JOIN account_invoice_stock_picking_rel as aispr ON aispr.stock_picking_id = sp.id 
                        LEFT JOIN account_invoice ai ON ai.id = aispr.account_invoice_id
                        LEFT JOIN stock_pack_operation as spo ON spo.picking_id = sp.id
                        where ai.id in (%s) and sp.state='done' order by sp.date_done DESC
                        """ % purchase_shipment_inv
                self.env.cr.execute(query)
                query_res = self.env.cr.dictfetchall()
            else:
                query = """
                select sp.name as name, sp.min_date as min_date, sp.date_done as date_done, spo.qty_done as qty_delivered from stock_picking as sp
                LEFT JOIN stock_pack_operation as spo ON spo.picking_id = sp.id
                where state='done' and sp.origin in (select name from sale_order as so
                LEFT JOIN pi_lc_rel as plr on plr.pi_id = so.lc_id
                where so.lc_id=%s) and sp.state='done'
                """ % lc_id
                self.env.cr.execute(query)
                query_res = self.env.cr.dictfetchall()
        else:
            query = """select distinct sp.name as name, sp.min_date as min_date, sp.date_done as date_done, spo.qty_done as qty_delivered from stock_picking as sp 
                        LEFT JOIN stock_pack_operation as spo ON spo.picking_id = sp.id
                        where origin='%s' and sp.state='done'
                            """ % so_name
            self.env.cr.execute(query)
            query_res = self.env.cr.dictfetchall()

        lc_delivery_details_str = ""
        ReportUtility = self.env['report.utility']
        for data in query_res:
            name = data['name'] if data['name'] is not None else ''
            min_date = datetime.strptime(data['min_date'], '%Y-%m-%d %H:%M:%S').date() if data[
                                                                                              'min_date'] is not None else ''
            qty = data["qty_delivered"] if data["qty_delivered"] is not None else '0'
            delivery_date = ReportUtility.get_date_from_string(str(min_date))

            lc_delivery_details_str += str(name) + ", " + str(qty) + ", " + str(delivery_date) + "\n"
        date_done = ''
        if query_res:
            date_done_uniformat = datetime.strptime(query_res[0]['date_done'], '%Y-%m-%d %H:%M:%S').date() if data[
                                                                                                                  'date_done'] is not None else ''
            if date_done_uniformat:
                date_done = ReportUtility.get_date_from_string(str(date_done_uniformat))
        return lc_delivery_details_str, str(date_done)

    def get_lc_qty(self, lc_id):
        if lc_id:
            query = """
                    select SUM(product_qty) as lc_qty from lc_product_line where lc_id='%s'
                    """ % lc_id
            self.env.cr.execute(query)
            query_res = self.env.cr.dictfetchall()

            lc_qty = 0
            if query_res[0]['lc_qty'] is not None:
                lc_qty = query_res[0]['lc_qty']
            return lc_qty
        return 0

    def get_lc_pi_no(self, lc_id):
        if lc_id:
            query = """
            select name from proforma_invoice as pi LEFT JOIN pi_lc_rel AS plr ON pi.id = plr.pi_id where plr.lc_id='%s'
            """ % lc_id
            self.env.cr.execute(query)
            query_res = self.env.cr.dictfetchall()
            lc_pi_ids = ''
            for data in query_res:
                lc_pi_ids += data['name'] + ", "
            return lc_pi_ids
        return ''

    def get_lc_so_no(self, lc_id):
        if lc_id:
            query = """
            select name from sale_order as so LEFT JOIN pi_lc_rel AS plr ON so.pi_id = plr.pi_id where plr.lc_id='%s'
            """ % lc_id
            self.env.cr.execute(query)
            query_res = self.env.cr.dictfetchall()
            lc_so_ids = ''
            for data in query_res:
                lc_so_ids += data['name'] + ", "
            return lc_so_ids
        return ''

    def get_delivered_qty(self, lc_id):
        if lc_id:
            lc_id = self.env['letter.credit'].search([('id', '=', lc_id)])
            delivered_qty = 0
            for pi_id in lc_id.pi_ids_temp:
                so_ids = self.env['sale.order'].search([('pi_id', '=', pi_id.id)])
                for so_id in so_ids:
                    sols = so_id.order_line
                    for sol in sols:
                        delivered_qty += sol.qty_delivered
            return delivered_qty
        else:
            return 0

    def get_document_qty(self, lc_id):
        if lc_id:
            query = """
            select product_received_qty from lc_product_line where lc_id='%s'
            """ % lc_id
            self.env.cr.execute(query)
            query_res = self.env.cr.dictfetchall()
            document_qty = 0
            if query_res:
                document_qty = query_res[0]['product_received_qty']
            return document_qty
        return 0

    @staticmethod
    def get_sheet_header(sheet, docs, workbook, filter_by_text, type_text):
        title_format_center = workbook.add_format({'align': 'center', 'bold': False, 'size': 22, 'text_wrap': True})
        title_format_center.set_font_name('Times New Roman')
        sub_title_format_center = workbook.add_format({'align': 'center', 'bold': False, 'size': 10, 'text_wrap': True})
        sub_title_format_center.set_font_name('Times New Roman')
        subject_format_center = workbook.add_format({'align': 'center', 'bold': False, 'size': 15, 'text_wrap': True})
        subject_format_center.set_font_name('Times New Roman')
        header_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bold': True, 'size': 8, 'border': 1,
             'text_wrap': True})
        header_format_left.set_font_name('Times New Roman')

        company_id = docs[0].company_id
        street = docs[0].company_id.street
        street2 = docs[0].company_id.street2
        city_zip_country = docs[0].company_id.city + "-" + docs[0].company_id.zip + ", " + docs[
            0].company_id.country_id.name

        sheet.merge_range('A1:AS1', company_id.name, title_format_center)
        sheet.merge_range('A2:AS2', street, sub_title_format_center)
        sheet.merge_range('A3:AS3', street2, sub_title_format_center)
        sheet.merge_range('A4:AS4', city_zip_country, sub_title_format_center)
        sheet.merge_range('A5:AS5', "LC Register", subject_format_center)
        sheet.merge_range('A6:AS6', "Filter By: " + filter_by_text, header_format_left)
        sheet.merge_range('A7:AS7', "Type: " + type_text, header_format_left)

    def generate_xlsx_report(self, workbook, data, obj):

        filter_by = obj.filter_by
        acceptance_default_value = obj.acceptance_default_value
        type = obj.type

        domain = [('lc_id.region_type', '=', type)]
        if type == 'all':
            domain = ['|', ('lc_id.region_type', '=', 'local'), ('lc_id.region_type', '=', 'foreign')]
        docs = self.env['purchase.shipment'].search(domain)

        report_name = "LC Register Report"
        sheet = workbook.add_worksheet(report_name)
        # Then override any that you want.
        sheet.set_default_row(25)
        sheet.set_row(0, 30)
        sheet.set_row(1, 13)
        sheet.set_row(2, 13)
        sheet.set_row(3, 13)
        sheet.set_row(4, 18)
        sheet.set_row(5, 13)
        sheet.set_row(6, 13)
        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 15)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 4, 15)
        sheet.set_column(5, 5, 15)
        sheet.set_column(20, 20, 20)

        # FORMAT
        footer_border_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bold': True, 'size': 10})
        footer_border_format_left.set_font_name('Times New Roman')
        sub_header_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bg_color': '#81d41a', 'bold': False, 'size': 10, 'border': 1,
             'text_wrap': True})
        sub_header_format_left.set_font_name('Times New Roman')

        lc_static_issue_date = '01/01/2022'
        where = ''
        filter_by_text = ''
        if filter_by == 'goods_delivered_doc_not_prepared':
            filter_by_text = 'Goods Delivered but doc. not prepared'
            where += "where ps.doc_preparation_date is null and (ps.state = 'receive_doc' or ps.state = 'draft' ) and sol.qty_delivered > 0 "
        elif filter_by == 'first_acceptance':
            filter_by_text = '1st Acceptance'
            where += "where CURRENT_DATE-(Date(ps.to_buyer_date)) > " + acceptance_default_value + " and ps.to_first_acceptance_date is null "
        elif filter_by == 'second_acceptance':
            filter_by_text = "2nd Acceptance"
            where += "where CURRENT_DATE - (Date(ps.to_seller_bank_date)) > " + acceptance_default_value + " and ps.to_maturity_date is null "
        elif filter_by == 'maturated_but_amount_not_collect':
            filter_by_text = 'Matured but Amount not collected'
            where += "where ps.payment_rec_date is null and ps.to_maturity_date is not null "
        elif filter_by == 'percentage_of_first_acceptance_collection':
            filter_by_text = 'Percentage of First Acceptance Collection'
            where += "where ps.to_first_acceptance_date >= '" + obj.date_from + "' and ps.to_first_acceptance_date <= '" + obj.date_to + "' and ps.to_first_acceptance_date is not null and ps.to_buyer_date is not null "
        elif filter_by == 'lc_history':
            filter_by_text = 'LC Shipment History'
            where += "where ps.shipment_done_date >= '" + obj.date_from + "' and ps.shipment_done_date <= '" + obj.date_to + "' "

        type_text = ''
        where_so = ''
        if type == 'all':
            type_text = 'Local & Foreign'
            where += " and lc.region_type in ('local', 'foreign')"
            where_so += " and so.region_type in ('local', 'foreign')"
        elif type == 'local':
            type_text = 'Local'
            where += "and lc.region_type = 'local'"
            where_so += " and so.region_type = 'local'"
        elif type == 'foreign':
            type_text = 'Foreign'
            where += " and lc.region_type = 'foreign'"
            where_so += " and so.region_type = 'foreign'"

        if filter_by == 'lc_number':
            filter_by_text = 'LC Number: ' + obj.lc_number.name
            where += " where lc.id ='" + str(obj.lc_number.id) + "'"
        else:
            where += " and lc.issue_date >='" + lc_static_issue_date + "' "

        if filter_by == 'goods_delivered_but_lc_not_received':
            filter_by_text = 'Goods Delivered but LC not received'
            query = '''
                select so.id,rp.name as party_name, rp2.name as executive_name, sol.name as product_name, 
                so.region_type as region_type, so.name as so_name, 
                pi.name as pi_name,rc.name as currency, SUM(sol.qty_delivered) as qty_delivery,
                SUM(sol.product_uom_qty)-SUM(sol.qty_delivered) as undelivered_qty
                from sale_order as so 
                LEFT JOIN sale_order_type as sot on so.type_id = sot.id 
                LEFT JOIN sale_order_line as sol on so.id = sol.order_id
                LEFT JOIN res_partner as rp on rp.id = so.partner_id
                LEFT JOIN res_users as ru on ru.id = rp.user_id
                LEFT JOIN proforma_invoice as pi on pi.id = so.pi_id
                LEFT JOIN res_partner as rp2 on rp2.id = ru.partner_id
                LEFT JOIN product_pricelist as ppl on ppl.id = so.pricelist_id
                LEFT JOIN res_currency as rc on rc.id = ppl.currency_id
                where so.lc_id is null
                and sot.sale_order_type='lc_sales' and sol.qty_delivered > 0 %s 
                group by so.id,party_name,executive_name,product_name,so.region_type,so_name,pi_name,currency
            ''' % where_so
        elif filter_by == 'shipment_date_expired_but_goods_undelivered':
            filter_by_text = 'Shipment date expired but goods undelivered'
            query = '''
                SELECT distinct ps.id, MAX(rp.name) as party_name,MAX(rp2.name) as executive_name,MAX(lpl.name) as product_name, MAX(lc.name) as lc_number, 
                MAX(ps.name) as shipment_no, SUM(coalesce(spl.product_qty,0)) as shipment_qty, SUM(coalesce(ps.invoice_value,0)) as shipment_amount, MAX(lc.tenure) as tenure,
                MAX(ps.bl_date) as doc_dispatch_to_party_date_foreign,MAX(coalesce((CURRENT_DATE-ps.bl_date),0)) as aging_first_acceptance_days_foreign,
                MAX(date(ps.to_first_acceptance_date + INTERVAL '7 day')) as to_buyer_bank_date_foreign,
                MAX(ps.to_buyer_bank_date) as to_buyer_bank_date,MAX(ps.to_seller_bank_date) as to_seller_bank_date,
                MAX(coalesce((CURRENT_DATE-ps.to_seller_bank_date),0)) as aging_2nd_acceptance_days, 
                MAX(rc.name) as currency, 
                MAX(lc.id) as lc_id, MAX(lc.shipment_date) as shipment_date, MAX(lc.expiry_date) as expiry_date, MAX(ps.doc_preparation_date) as doc_preparation_date,
                MAX(lc.issue_date) as lc_date,MAX(coalesce(lc.lc_value,0)) as lc_amount,MAX(lc.region_type) as region_type,
                MAX(ps.to_buyer_date) as doc_dispatch_to_party_date, MAX(ps.to_first_acceptance_date) as first_acceptance_doc_submission_date,
                MAX(coalesce((CURRENT_DATE-ps.to_buyer_date),0)) as aging_first_acceptance_days,MAX(ps.to_maturity_date) as maturity_date, 
                MAX(ps.shipment_done_date) as shipment_done_date, 
                MAX(coalesce(ps.discrepancy_amount,0)) as discrepancy_amount, MAX(coalesce(ps.ait_amount,0)) as ait_amount, MAX(ps.payment_rec_date) as payment_rec_date, MAX(coalesce(ps.payment_rec_amount,0)) as payment_rec_amount, MAX(coalesce(ps.payment_charge,0)) as payment_charge, 
                MAX(ps.comment) as comment, MAX(lc.second_party_bank) as second_party_bank, MAX(rb.bic) as samuda_bank_name,
                MAX(pu.name) as packing_type, MAX(ps.bill_id) as bill_id_no, 
                SUM(coalesce(lpl.product_received_qty,0)) as document_qty,
                SUM(coalesce(lpl.product_qty,0)) as product_qty,
                MAX(coalesce((ps.to_first_acceptance_date-ps.to_buyer_date),0)) as percentage_of_first_acceptance,
                (select SUM(sol.qty_delivered) as qty_delivered 
                 from sale_order as so LEFT JOIN sale_order_line as sol ON so.id = sol.order_id 
                     where so.pi_id=bit_and(plr.pi_id)) as pp1, SUM(spl.product_qty) as pp2,
                (SUM(spl.product_qty) - (select SUM(sol.qty_delivered) as qty_delivered 
                 from sale_order as so LEFT JOIN sale_order_line as sol ON so.id = sol.order_id 
                     where so.pi_id=bit_and(plr.pi_id))) as pp
                FROM purchase_shipment AS ps 
                LEFT JOIN letter_credit AS lc ON ps.lc_id = lc.id
                LEFT JOIN res_partner AS rp ON rp.id = lc.second_party_applicant
                LEFT JOIN res_users AS ru ON ru.id = rp.user_id
                LEFT JOIN res_partner AS rp2 ON rp2.id = ru.partner_id
                LEFT JOIN lc_product_line AS lpl ON lpl.lc_id = ps.lc_id
                LEFT JOIN res_currency as rc ON rc.id = lc.currency_id
                LEFT JOIN shipment_product_line AS spl ON ps.id = spl.shipment_id
                LEFT JOIN res_partner_bank AS rpb ON rpb.id = lc.first_party_bank_acc
                LEFT JOIN res_bank AS rb ON rb.id = rpb.bank_id
                LEFT JOIN product_uom AS pu ON pu.id = ps.count_uom 
                LEFT JOIN pi_lc_rel as plr ON plr.lc_id = lc.id
                LEFT JOIN sale_order as so ON so.pi_id = plr.pi_id
                LEFT JOIN sale_order_line as sol ON sol.order_id = so.id
                where lc.shipment_date < CURRENT_DATE  
                and spl.product_qty-(select SUM(sol.qty_delivered) as qty_delivered 
                 from sale_order as so LEFT JOIN sale_order_line as sol ON so.id = sol.order_id 
                     where so.lc_id=lc.id) > 0 %s group by ps.id
                            ''' % where_so
        else:
            query = '''
                    SELECT distinct ps.id, MAX(rp.name) as party_name,MAX(rp2.name) as executive_name,MAX(lpl.name) as product_name, MAX(lc.name) as lc_number, 
                    MAX(ps.name) as shipment_no, SUM(coalesce(spl.product_qty,0)) as shipment_qty, SUM(coalesce(ps.invoice_value,0)) as shipment_amount, MAX(lc.tenure) as tenure,
                    MAX(ps.bl_date) as doc_dispatch_to_party_date_foreign,MAX(coalesce((CURRENT_DATE-ps.bl_date),0)) as aging_first_acceptance_days_foreign,
                    MAX(date(ps.to_first_acceptance_date + INTERVAL '7 day')) as to_buyer_bank_date_foreign,
                    MAX(ps.to_buyer_bank_date) as to_buyer_bank_date,MAX(ps.to_seller_bank_date) as to_seller_bank_date,
                    MAX(coalesce((CURRENT_DATE-ps.to_seller_bank_date),0)) as aging_2nd_acceptance_days, 
                    MAX(rc.name) as currency, 
                    MAX(lc.id) as lc_id, MAX(lc.shipment_date) as shipment_date, MAX(lc.expiry_date) as expiry_date, MAX(ps.doc_preparation_date) as doc_preparation_date,
                    MAX(lc.issue_date) as lc_date,MAX(coalesce(lc.lc_value,0)) as lc_amount,MAX(lc.region_type) as region_type,
                    MAX(ps.to_buyer_date) as doc_dispatch_to_party_date, MAX(ps.to_first_acceptance_date) as first_acceptance_doc_submission_date,
                    MAX(coalesce((CURRENT_DATE-ps.to_buyer_date),0)) as aging_first_acceptance_days,MAX(ps.to_maturity_date) as maturity_date, 
                    MAX(ps.shipment_done_date) as shipment_done_date, 
                    MAX(coalesce(ps.discrepancy_amount,0)) as discrepancy_amount, MAX(coalesce(ps.ait_amount,0)) as ait_amount, MAX(ps.payment_rec_date) as payment_rec_date, MAX(coalesce(ps.payment_rec_amount,0)) as payment_rec_amount, MAX(coalesce(ps.payment_charge,0)) as payment_charge, 
                    MAX(ps.comment) as comment, MAX(lc.second_party_bank) as second_party_bank, MAX(rb.bic) as samuda_bank_name,
                    MAX(pu.name) as packing_type, MAX(ps.bill_id) as bill_id_no, MAX(coalesce(lpl.product_received_qty,0)) as document_qty,
                    SUM(coalesce(lpl.product_qty,0)) as product_qty,
                    MAX(coalesce((ps.to_first_acceptance_date-ps.to_buyer_date),0)) as percentage_of_first_acceptance
                    FROM purchase_shipment AS ps 
                    LEFT JOIN letter_credit AS lc ON ps.lc_id = lc.id
                    LEFT JOIN res_partner AS rp ON rp.id = lc.second_party_applicant
                    LEFT JOIN res_users AS ru ON ru.id = rp.user_id
                    LEFT JOIN res_partner AS rp2 ON rp2.id = ru.partner_id
                    LEFT JOIN lc_product_line AS lpl ON lpl.lc_id = ps.lc_id
                    LEFT JOIN res_currency as rc ON rc.id = lc.currency_id
                    LEFT JOIN shipment_product_line AS spl ON ps.id = spl.shipment_id
                    LEFT JOIN res_partner_bank AS rpb ON rpb.id = lc.first_party_bank_acc
                    LEFT JOIN res_bank AS rb ON rb.id = rpb.bank_id
                    LEFT JOIN product_uom AS pu ON pu.id = ps.count_uom 
                    LEFT JOIN pi_lc_rel as plr ON plr.lc_id = lc.id
                    LEFT JOIN sale_order as so ON so.pi_id = plr.pi_id
                    LEFT JOIN sale_order_line as sol ON sol.order_id = so.id
                    ''' + where + ''' group by ps.id '''
        self.env.cr.execute(query)
        datas_excel = self.env.cr.dictfetchall()

        # SHEET HEADER
        self.get_sheet_header(sheet, docs, workbook, filter_by_text, type_text)

        self.get_sheet_table_head(sheet, workbook)

        self.set_sheet_table_data(obj, sheet, workbook, datas_excel)

        data['name'] = report_name


LcRegisterXLSX('report.lc_sales_local_report.lc_register_report',
               'lc.register.wizard', parser=report_sxw.rml_parse)
