from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.tools.misc import formatLang
import math


class MonthlyOtSheetXLSX(ReportXlsx):
    _report_name = "Monthly OT Report"

    def _get_report_sheet(self, workbook):
        sheet = workbook.add_worksheet(self._report_name)
        # Then override any that you want.
        sheet.set_row(0, 30)
        sheet.set_row(5, 35)
        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 15)
        return sheet

    def _get_sheet_header(self, sheet, docs, workbook):
        title_format_center = workbook.add_format({'align': 'center', 'bold': False, 'size': 22, 'text_wrap': True})
        title_format_center.set_font_name('Times New Roman')
        subject_format_center = workbook.add_format({'align': 'center', 'bold': False, 'size': 15, 'text_wrap': True})
        subject_format_center.set_font_name('Times New Roman')
        name_format_left_int = workbook.add_format(
            {'align': 'left', 'border': 1, 'bold': False, 'size': 8, 'text_wrap': True})
        name_format_left_int.set_font_name('Times New Roman')
        name_format_left = workbook.add_format({'align': 'left', 'bold': False, 'size': 10})
        name_format_left.set_font_name('Times New Roman')

        sheet.merge_range('A1:R1', docs.operating_unit_id.company_id.name, title_format_center)
        sheet.merge_range('A2:R2', "Monthly Overtime Sheet", subject_format_center)
        sheet.merge_range('A3:R3', "Operating Unit: " + str(docs.operating_unit_id.name), name_format_left)
        sheet.merge_range('A4:R4', "Initiated by: " + "HR & Admin", name_format_left)
        sheet.merge_range('A5:R5', "Overtime Cycle: " + self.env['report.utility'].get_date_from_string(
            docs.date_start) + ' to ' + self.env['report.utility'].get_date_from_string(docs.date_end),
                          name_format_left)

    def _get_sheet_table_header(self, sheet, workbook):
        header_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bg_color': '#FFC000', 'bold': False, 'size': 10, 'border': 1,
             'text_wrap': True})
        header_format_left.set_font_name('Times New Roman')

        sheet.write(5, 0, "Sl.No.", header_format_left)
        sheet.write(5, 1, "Name", header_format_left)
        sheet.write(5, 2, "Designation", header_format_left)
        sheet.write(5, 3, "Date  of Joining", header_format_left)
        sheet.write(5, 4, "ID No.", header_format_left)
        sheet.write(5, 5, "Basic Salary 40%", header_format_left)
        sheet.write(5, 6, "House Rent 70% of Basic", header_format_left)
        sheet.write(5, 7, "Medical Allowance 30% of Basic", header_format_left)
        sheet.write(5, 8, "Convince Allowance 30% of Basic", header_format_left)
        sheet.write(5, 9, "Other Allowance 20% of Basic", header_format_left)
        sheet.write(5, 10, "Gross", header_format_left)
        sheet.write(5, 11, "Total Overtime Hour", header_format_left)
        sheet.write(5, 12, "Overtime Rate/Hour", header_format_left)
        sheet.write(5, 13, "Total OT Earning Amount", header_format_left)
        sheet.write(5, 14, "Others/ Arrear", header_format_left)
        sheet.write(5, 15, "Total", header_format_left)
        sheet.write(5, 16, "Deduction", header_format_left)
        sheet.write(5, 17, "Net Payable", header_format_left)

    def _get_table_dataset(self, docs):
        department = self.env['hr.department'].search([])
        dpt_payslips_list = []

        for d in department:
            dpt_payslips = {'name': d.name, 'seq': d.sequence, 'val': []}
            payslip_filter_data = list(filter(lambda x: x.employee_id.department_id.id == d.id, docs.slip_ids))
            for slip in payslip_filter_data:
                payslip = {}

                payslip['emp_name'] = slip.employee_id.name
                payslip['designation'] = slip.employee_id.job_id.name
                payslip['doj'] = self.env['report.utility'].get_date_from_string(
                    slip.employee_id.initial_employment_date)

                gross = math.ceil((slip.employee_id.contract_id.wage) * 2.5)
                payslip['gross'] = gross
                payslip['gross_float'] = gross
                payslip['emp_id'] = slip.employee_id.device_employee_acc
                payslip['basic_40'] = slip.employee_id.contract_id.wage
                payslip['basic_70'] = (slip.employee_id.contract_id.wage * 0.70)
                payslip['basic_30'] = (slip.employee_id.contract_id.wage * 0.30)
                payslip['basic_20'] = (slip.employee_id.contract_id.wage * 0.20)
                obj_number_of_hours = list(filter(lambda x: x.code == 'OT', slip.worked_days_line_ids))
                number_of_hours = 0
                if obj_number_of_hours:
                    number_of_hours = obj_number_of_hours[0].number_of_hours
                payslip['number_of_hours'] = number_of_hours

                # OT Rate
                ot_rate = (slip.employee_id.contract_id.wage + payslip['basic_70'] + payslip['basic_30'] + payslip[
                    'basic_30'] + payslip['basic_20']) / 208
                payslip['ot_rate_hour'] = ot_rate
                payslip['ot_earning_amount'] = round(number_of_hours * ot_rate)
                obj_ot_arrear = list(filter(lambda x: x.code == 'ARSOT', slip.input_line_ids))
                arrear = 0
                if obj_ot_arrear:
                    arrear = obj_ot_arrear[0].amount
                payslip['arrear'] = arrear
                payslip['total'] = payslip['ot_earning_amount'] + payslip['arrear']

                obj_ot_deduction = list(filter(lambda x: x.code == 'ODSOT', slip.input_line_ids))
                deduction = 0
                if obj_ot_deduction:
                    deduction = obj_ot_deduction[0].amount
                payslip['deduction'] = deduction
                payslip['total_payable'] = payslip['total'] - payslip['deduction']
                dpt_payslips['val'].append(payslip)

            emp_sort_list = dpt_payslips['val']

            dpt_payslips['val'] = emp_sort_list
            dpt_payslips_list.append(dpt_payslips)
        return dpt_payslips_list

    def _set_sheet_table_data(self, sheet, workbook, dpt_payslips_list):
        sub_header_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bg_color': '#ffffff', 'bold': True, 'size': 10, 'border': 1,
             'text_wrap': False})
        sub_header_format_left.set_font_name('Times New Roman')
        name_border_format_colored_int = workbook.add_format(
            {'align': 'left', 'border': 1, 'valign': 'vcenter', 'bold': False, 'size': 8})
        name_border_format_colored_right_int = workbook.add_format(
            {'align': 'right', 'border': 1, 'valign': 'vcenter', 'bold': False, 'size': 8})
        name_border_format_colored = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'right', 'border': 1, 'valign': 'vcenter', 'bold': False, 'size': 8})
        name_border_format_colored.set_font_name('Times New Roman')

        row = 5
        sl = 0
        total_basic_40 = 0.0
        total_basic_70 = 0.0
        total_basic_30 = 0.0
        total_basic_20 = 0.0
        total_gross = 0.0
        over_time_hours = 0.0
        total_over_time_rate = 0.0
        ot_earning_amount = 0.0
        total_arrear = 0.0
        total_amount = 0.0
        total_deduction = 0.0
        total_net_payable = 0.0

        for department_emp in dpt_payslips_list:
            department_serial = 0
            department_wise_val = department_emp.get('val')
            for emp in department_wise_val:
                if emp.get('ot_earning_amount') > 0:
                    if department_serial == 0:
                        row += 1
                        department_serial += 1
                        dpt_name = department_emp.get('name')
                        sheet.write(row, 0, dpt_name, sub_header_format_left)

                    row += 1
                    sl += 1
                    sheet.write(row, 0, sl, name_border_format_colored_right_int)
                    sheet.write(row, 1, emp.get('emp_name'), name_border_format_colored_int)
                    sheet.write(row, 2, emp.get('designation'), name_border_format_colored_int)
                    sheet.write(row, 3, emp.get('doj'), name_border_format_colored_int)
                    sheet.write(row, 4, emp.get('emp_id'), name_border_format_colored_int)
                    sheet.write(row, 5, emp.get('basic_40'), name_border_format_colored)
                    sheet.write(row, 6, emp.get('basic_70'), name_border_format_colored)
                    sheet.write(row, 7, emp.get('basic_30'), name_border_format_colored)
                    sheet.write(row, 8, emp.get('basic_30'), name_border_format_colored)
                    sheet.write(row, 9, emp.get('basic_20'), name_border_format_colored)
                    sheet.write(row, 10, emp.get('gross'), name_border_format_colored)
                    sheet.write(row, 11, emp.get('number_of_hours'), name_border_format_colored)
                    sheet.write(row, 12, emp.get('ot_rate_hour'), name_border_format_colored)
                    sheet.write(row, 13, emp.get('ot_earning_amount'), name_border_format_colored)
                    sheet.write(row, 14, emp.get('arrear'), name_border_format_colored)
                    sheet.write(row, 15, emp.get('total'), name_border_format_colored)
                    sheet.write(row, 16, emp.get('deduction'), name_border_format_colored)
                    sheet.write(row, 17, emp.get('total_payable'), name_border_format_colored)

                    # Footer Total
                    total_basic_40 += emp.get('basic_40')
                    total_basic_70 += emp.get('basic_70')
                    total_basic_30 += emp.get('basic_30')
                    total_basic_20 += emp.get('basic_20')
                    total_gross += emp.get('gross_float')
                    over_time_hours += emp.get('number_of_hours')
                    total_over_time_rate += emp.get('ot_rate_hour')
                    ot_earning_amount += emp.get('ot_earning_amount')
                    total_arrear += emp.get('arrear')
                    total_amount += emp.get('total')
                    total_deduction += emp.get('deduction')
                    total_net_payable += emp.get('total_payable')

            footer_data = {
                'row': row,
                'total_basic_40': total_basic_40,
                'total_basic_70': total_basic_70,
                'total_basic_30': total_basic_30,
                'total_basic_20': total_basic_20,
                'total_gross': total_gross,
                'over_time_hours': over_time_hours,
                'total_over_time_rate': total_over_time_rate,
                'ot_earning_amount': ot_earning_amount,
                'total_arrear': total_arrear,
                'total_amount': total_amount,
                'total_deduction': total_deduction,
                'total_net_payable': total_net_payable
            }
        return footer_data

    def _set_footer_data(self, sheet, workbook, footer_dataset):
        footer_border_format_right = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'right', 'bold': True, 'size': 10})
        footer_border_format_right.set_font_name('Times New Roman')

        row = footer_dataset['row']
        row += 1
        sheet.merge_range('A' + str(row + 1) + ':C' + str(row + 1) + '', 'Total', footer_border_format_right)
        sheet.write(row, 3, '', footer_border_format_right)
        sheet.write(row, 4, '', footer_border_format_right)
        sheet.write(row, 5, footer_dataset['total_basic_40'], footer_border_format_right)
        sheet.write(row, 6, footer_dataset['total_basic_70'], footer_border_format_right)
        sheet.write(row, 7, footer_dataset['total_basic_30'], footer_border_format_right)
        sheet.write(row, 8, footer_dataset['total_basic_30'], footer_border_format_right)
        sheet.write(row, 9, footer_dataset['total_basic_20'], footer_border_format_right)
        sheet.write(row, 10, footer_dataset['total_gross'], footer_border_format_right)
        sheet.write(row, 11, footer_dataset['over_time_hours'], footer_border_format_right)
        sheet.write(row, 12, footer_dataset['total_over_time_rate'], footer_border_format_right)
        sheet.write(row, 13, footer_dataset['ot_earning_amount'], footer_border_format_right)
        sheet.write(row, 14, footer_dataset['total_arrear'], footer_border_format_right)
        sheet.write(row, 15, footer_dataset['total_amount'], footer_border_format_right)
        sheet.write(row, 16, footer_dataset['total_deduction'], footer_border_format_right)
        sheet.write(row, 17, footer_dataset['total_net_payable'], footer_border_format_right)

        # Total Amount
        row += 2
        sheet.write(row, 15, 'Total', footer_border_format_right)
        sheet.write(row, 17, footer_dataset['total_net_payable'], footer_border_format_right)

        # In Words
        footer_border_format_right = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'right', 'bold': True, 'size': 8, 'text_wrap': False})

        if footer_dataset['total_net_payable'] > 0:
            amt_to_word = self.env['res.currency'].amount_to_word(float(footer_dataset['total_net_payable']))
            row += 2
            sheet.write(row, 17, 'In Words:' + amt_to_word, footer_border_format_right)

        # Signature
        name_format_left = workbook.add_format({'align': 'left', 'bold': False, 'size': 10})
        name_format_left.set_font_name('Times New Roman')
        row += 3
        sheet.write(row, 1, 'Prepared by', name_format_left)
        sheet.write(row, 4, 'Checked by', name_format_left)
        sheet.write(row, 8, 'Recommended by', name_format_left)
        sheet.write(row, 11, 'Authorized by', name_format_left)
        sheet.write(row, 15, 'Approved by', name_format_left)

    def generate_xlsx_report(self, workbook, data, obj):
        docs = obj.hr_payslip_run_id
        sheet = self._get_report_sheet(workbook)

        # SHEET HEADER
        self._get_sheet_header(sheet, docs, workbook)

        # SHEET TABLE HEADER
        self._get_sheet_table_header(sheet, workbook)
        dpt_payslips_list = self._get_table_dataset(docs)
        get_footer_dataset = self._set_sheet_table_data(sheet, workbook, dpt_payslips_list)

        self._set_footer_data(sheet, workbook, get_footer_dataset)


MonthlyOtSheetXLSX('report.hr_payroll_ot.monthly_ot_sheet_xlsx',
                   'ot.report.wizard', parser=report_sxw.rml_parse)
