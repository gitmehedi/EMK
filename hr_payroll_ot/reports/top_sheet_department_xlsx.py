from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.tools.misc import formatLang
from dateutil.relativedelta import relativedelta
from datetime import datetime
import math

class TopSheetDepartmentXLSX(ReportXlsx):

    def _get_sheet_header(self, docs, workbook):
        company_id = docs.operating_unit_id.company_id
        report_name = "Top Sheet (Department)"
        sheet = workbook.add_worksheet(report_name)
        sheet.set_row(0, 30)
        sheet.set_row(6, 30)
        sheet.set_column(0, 0, 18)
        sheet.set_default_row(22)

        title_format_center = workbook.add_format({'align': 'center', 'bold': True, 'size': 22, 'text_wrap': True})
        title_format_center.set_font_name('Times New Roman')
        name_format_left = workbook.add_format(
            {'num_format': '#,##0.00', 'align': 'left', 'bold': False, 'size': 10, 'text_wrap': False})
        name_format_left.set_font_name('Times New Roman')
        subject_format_center = workbook.add_format({'align': 'center', 'bold': True, 'size': 10, 'text_wrap': True})
        subject_format_center.set_font_name('Times New Roman')

        sheet.merge_range('A1:O1', company_id.name, title_format_center)
        sheet.merge_range('A2:O2', str(docs.date_start), name_format_left)
        sheet.merge_range('A3:O3', "Initiated by : Human Resources", name_format_left)
        sheet.merge_range('A4:O4', "To : Managing Director", name_format_left)
        sheet.merge_range('A5:O5', "Money Requisition for Disbursement of Overtime Salary: " + docs.name + "",
                          subject_format_center)
        return sheet

    def _set_sheet_table_header(self, sheet, workbook):
        header_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bg_color': '#FFC000', 'bold': False, 'size': 8, 'border': 1, 'text_wrap': True})
        header_format_left.set_font_name('Times New Roman')

        sheet.write(6, 0, "Department", header_format_left)
        sheet.write(6, 1, "No of Employee", header_format_left)
        sheet.write(6, 2, "Basic", header_format_left)
        sheet.write(6, 3, "House Rent Allowance (70% of Basic)", header_format_left)
        sheet.write(6, 4, "Medical Allowance (30% of Basic)", header_format_left)
        sheet.write(6, 5, "Conveyance Allowance (30% of Basic)", header_format_left)
        sheet.write(6, 6, "Others (20% of Basic)", header_format_left)
        sheet.write(6, 7, "Gross", header_format_left)
        sheet.write(6, 8, "Total Overtime Hour", header_format_left)
        sheet.write(6, 9, "Overtime Rate/Hour", header_format_left)
        sheet.write(6, 10, "Total OT Earning Amount", header_format_left)
        sheet.write(6, 11, "Others/ Arrear", header_format_left)
        sheet.write(6, 12, "Total", header_format_left)
        sheet.write(6, 13, "Deduction", header_format_left)
        sheet.write(6, 14, "Total Payable", header_format_left)
        return sheet

    def _set_footer_value_n_signature(self, docs, sheet, row, workbook, footer_total_payable):
        name_format_left = workbook.add_format(
            {'num_format': '#,##0.00', 'align': 'left', 'bold': False, 'size': 10, 'text_wrap': False})
        name_format_left.set_font_name('Times New Roman')
        footer_name_format_right_without_border = workbook.add_format(
            {'num_format': '#,##0.00', 'align': 'left', 'bold': True, 'size': 8, 'font_color': 'black'})
        footer_name_format_right_without_border.set_font_name('Times New Roman')

        if footer_total_payable > 0:
            amt_to_word = self.env['res.currency'].amount_to_word(float(footer_total_payable))
            row += 3
            sheet.merge_range('A' + str(row + 1) + ':C' + str(row + 1) + '', 'Cash Payment:', name_format_left)
            sheet.merge_range('D' + str(row + 1) + ':E' + str(row + 1) + '', footer_total_payable, name_format_left)
            sheet.merge_range('F' + str(row + 1) + ':M' + str(row + 1) + '', amt_to_word, name_format_left)
            row += 1
            sheet.merge_range('A' + str(row + 1) + ':C' + str(row + 1) + '', 'Total fund Required:', name_format_left)
            sheet.merge_range('D' + str(row + 1) + ':E' + str(row + 1) + '', footer_total_payable, name_format_left)
            sheet.merge_range('F' + str(row + 1) + ':M' + str(row + 1) + '', amt_to_word, name_format_left)



        row += 2
        previous_month_payable = 0
        date_start = datetime.strptime(docs.date_start, "%Y-%m-%d")
        prev_month_start = date_start - relativedelta(months=1)
        hr_payslip_runs = self.env['hr.payslip.run'].search([('date_start', '=', prev_month_start), ('operating_unit_id', '=', docs.operating_unit_id.id), ('type', '=', '2')])
        for paylslip_run in hr_payslip_runs:
            previous_month_payable += paylslip_run.total_payable

        sheet.merge_range('A' + str(row + 1) + ':C' + str(row + 1) + '', 'Previous Month Net Payable was:', name_format_left)
        sheet.merge_range('D' + str(row + 1) + ':E' + str(row + 1) + '', previous_month_payable, footer_name_format_right_without_border)

        # Signature
        row += 3
        sheet.write(row, 1, 'Prepared by', name_format_left)
        sheet.write(row, 4, 'Checked by', name_format_left)
        sheet.write(row, 7, 'Recommended by', name_format_left)
        sheet.write(row, 10, 'Authorized by', name_format_left)
        sheet.write(row, 13, 'Approved by', name_format_left)

    def generate_xlsx_report(self, workbook, data, obj):
        docs = obj.hr_payslip_run_id
        sheet = self._get_sheet_header(docs, workbook)

        self._set_sheet_table_header(sheet, workbook)

        name_format_left_font_11 = workbook.add_format(
            {'num_format': '#,##0.00', 'align': 'left', 'bold': False, 'size': 11, 'text_wrap': True})
        name_format_left_font_11.set_font_name('Times New Roman')
        name_format_left_int = workbook.add_format({'align': 'left', 'border': 1, 'bold': False, 'size': 8, 'text_wrap': True})
        name_format_left_int.set_font_name('Times New Roman')

        footer_name_format_right = workbook.add_format(
            {'num_format': '#,##0.00', 'align': 'right', 'border': 1, 'bold': True, 'size': 8, 'font_color': 'black'})
        footer_name_format_right.set_font_name('Times New Roman')

        name_border_format_colored = workbook.add_format(
            {'num_format': '#,###0.00','align': 'right', 'border': 1,  'valign': 'vcenter', 'bold': False, 'size': 8})
        name_border_format_colored.set_font_name('Times New Roman')
        name_border_format_colored_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'border': 1, 'valign': 'vcenter', 'bold': False, 'size': 8})
        name_border_format_colored_left.set_font_name('Times New Roman')

        departments = self.env['hr.department'].search([])
        row = 7
        footer_employee = 0
        footer_basic = 0
        footer_basic_70 = 0
        footer_basic_30 = 0
        footer_basic_20 = 0
        footer_gross = 0
        footer_numner_of_hours = 0
        footer_ot_rate = 0
        footer_ot_earning_amount = 0
        footer_arrear = 0
        footer_total = 0
        footer_deduction = 0
        footer_total_payable = 0

        for department in departments:
            emp_count = 0
            basic = 0.0
            basic_70 = 0.0
            basic_30 = 0.0
            basic_20 = 0.0
            gross = 0.0
            number_of_hours = 0.0
            ot_rate = 0.0
            ot_earning_amount = 0
            ot_arrear = 0.0
            total = 0.0
            deduction = 0.0
            total_payable = 0.0

            payslip_filter_data = list(filter(lambda x: x.employee_id.department_id.id == department.id, docs.slip_ids))
            for slip in payslip_filter_data:
                obj_number_of_hours = list(filter(lambda x: x.code == 'OT', slip.worked_days_line_ids))
                if obj_number_of_hours:
                    if obj_number_of_hours[0].number_of_hours > 0:
                        number_of_hours += obj_number_of_hours[0].number_of_hours
                        emp_count += 1
                        basic += slip.employee_id.contract_id.wage
                        basic_70 += (slip.employee_id.contract_id.wage * 70) / 100
                        basic_30 += (slip.employee_id.contract_id.wage * 30) / 100
                        basic_20 += (slip.employee_id.contract_id.wage * 20) / 100
                        gross += math.ceil((slip.employee_id.contract_id.wage) * 2.5)

                        ot_rate += (basic + basic_70 + basic_30 + basic_30 + basic_20)/208
                        ot_earning_amount += round(number_of_hours * ot_rate)
                        obj_ot_arrear = list(filter(lambda x: x.code == 'ARSOT', slip.input_line_ids))
                        ot_arrear = 0
                        if obj_ot_arrear:
                            ot_arrear += obj_ot_arrear[0].amount
                        total += ot_earning_amount + ot_arrear
                        obj_ot_deduction = list(filter(lambda x: x.code == 'ODSOT', slip.input_line_ids))
                        deduction = 0
                        if obj_ot_deduction:
                            deduction += obj_ot_deduction[0].amount
                        total_payable += total - deduction

                        footer_employee += emp_count
                        footer_basic += basic
                        footer_basic_70 += basic_70
                        footer_basic_30 += basic_30
                        footer_basic_20 += basic_20
                        footer_gross += gross
                        footer_numner_of_hours += number_of_hours
                        footer_ot_rate += ot_rate
                        footer_ot_earning_amount += ot_earning_amount
                        footer_arrear += ot_arrear
                        footer_total += total
                        footer_deduction += deduction
                        footer_total_payable += total_payable
            if emp_count > 0 and number_of_hours > 0:
                sheet.write(row, 0, department.name, name_border_format_colored_left)
                sheet.write(row, 1, emp_count, name_format_left_int)
                sheet.write(row, 2, basic, name_border_format_colored)
                sheet.write(row, 3, basic_70, name_border_format_colored)
                sheet.write(row, 4, basic_30, name_border_format_colored)
                sheet.write(row, 5, basic_30, name_border_format_colored)
                sheet.write(row, 6, basic_20, name_border_format_colored)
                sheet.write(row, 7, gross, name_border_format_colored)
                sheet.write(row, 8, number_of_hours, name_border_format_colored)
                sheet.write(row, 9, ot_rate, name_border_format_colored)
                sheet.write(row, 10, ot_earning_amount, name_border_format_colored)
                sheet.write(row, 11, ot_arrear, name_border_format_colored)
                sheet.write(row, 12, total, name_border_format_colored)
                sheet.write(row, 13, deduction, name_border_format_colored)
                sheet.write(row, 14, total_payable, name_border_format_colored)
                row += 1


        # Total
        sheet.write(row, 0, 'Total', footer_name_format_right)
        sheet.write(row, 1, footer_employee, footer_name_format_right)
        sheet.write(row, 2, footer_basic, footer_name_format_right)
        sheet.write(row, 3, footer_basic_70, footer_name_format_right)
        sheet.write(row, 4, footer_basic_30, footer_name_format_right)
        sheet.write(row, 5, footer_basic_30, footer_name_format_right)
        sheet.write(row, 6, footer_basic_20, footer_name_format_right)
        sheet.write(row, 7, footer_gross, footer_name_format_right)
        sheet.write(row, 8, footer_numner_of_hours, footer_name_format_right)
        sheet.write(row, 9, footer_ot_rate, footer_name_format_right)
        sheet.write(row, 10, footer_ot_earning_amount, footer_name_format_right)
        sheet.write(row, 11, footer_arrear, footer_name_format_right)
        sheet.write(row, 12, footer_total, footer_name_format_right)
        sheet.write(row, 13, footer_deduction, footer_name_format_right)
        sheet.write(row, 14, footer_total_payable, footer_name_format_right)

        self._set_footer_value_n_signature(docs, sheet, row, workbook, footer_total_payable)

TopSheetDepartmentXLSX('report.hr_payroll_ot.top_sheet_department_xlsx',
                   'ot.report.wizard', parser=report_sxw.rml_parse)