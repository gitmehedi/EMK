from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
import math


class ReportFormat:
    def __init__(self, workbook):
        self.workbook = workbook

    def title(self):
        return self.workbook.add_format({'align': 'center', 'bold': True, 'size': 22, 'text_wrap': True})

    def text_align_left(self):
        return self.workbook.add_format(
            {'num_format': '#,##0.00', 'align': 'left', 'bold': False, 'size': 10, 'text_wrap': False})

    def text_align_right(self):
        return self.workbook.add_format(
            {'num_format': '#,##0.00', 'align': 'right', 'bold': False, 'size': 10, 'text_wrap': False})

    def text_align_right_bold(self):
        return self.workbook.add_format({'num_format': '#,##0.00', 'align': 'right', 'border': 1, 'bold': True, 'size': 8, 'font_color': 'black'})

    def text_align_center_bold_text_wrap(self):
        return self.workbook.add_format({'align': 'center', 'bold': True, 'size': 10, 'text_wrap': True})

    def text_align_right_with_border(self):
        return self.workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'right', 'border': 1, 'valign': 'vcenter', 'bold': False, 'size': 8})

    def text_align_left_with_border(self):
        return self.workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'border': 1, 'valign': 'vcenter', 'bold': False, 'size': 10})

    def table_header_bold_text_wrap(self):
        return self.workbook.add_format(
            {'align': 'left', 'bg_color': '#FFC000', 'bold': False, 'size': 8, 'border': 1, 'text_wrap': True})

    def numeric(self):
        return self.workbook.add_format({'align': 'right', 'border': 1, 'bold': False, 'size': 8, 'text_wrap': True})


class TopSheetDepartmentXLSX(ReportXlsx):
    def _get_sheet_header(self, docs, workbook):
        reportFormat = ReportFormat(workbook)
        company_id = docs.operating_unit_id.company_id
        report_name = "Top Sheet (Department)"
        sheet = workbook.add_worksheet(report_name)
        sheet.set_row(0, 30)
        sheet.set_row(6, 30)
        sheet.set_column(0, 0, 18)
        sheet.set_default_row(22)

        sheet.merge_range('A1:O1', company_id.name, reportFormat.title())
        sheet.merge_range('A2:O2', self.env['report.utility'].get_date_from_string(str(date.today())),
                          reportFormat.text_align_left())
        sheet.merge_range('A3:O3', "Initiated by : Human Resources", reportFormat.text_align_left())
        sheet.merge_range('A4:O4', "To : Managing Director", reportFormat.text_align_left())
        sheet.merge_range('A5:O5', "Money Requisition for Disbursement of Overtime Salary: " + docs.name + "",
                          reportFormat.text_align_center_bold_text_wrap())
        return sheet

    def _set_sheet_table_header(self, sheet, workbook):
        reportFormat = ReportFormat(workbook)
        sheet.write(6, 0, "Department", reportFormat.table_header_bold_text_wrap())
        sheet.write(6, 1, "No of Employee", reportFormat.table_header_bold_text_wrap())
        sheet.write(6, 2, "Basic", reportFormat.table_header_bold_text_wrap())
        sheet.write(6, 3, "House Rent Allowance (70% of Basic)", reportFormat.table_header_bold_text_wrap())
        sheet.write(6, 4, "Medical Allowance (30% of Basic)", reportFormat.table_header_bold_text_wrap())
        sheet.write(6, 5, "Conveyance Allowance (30% of Basic)", reportFormat.table_header_bold_text_wrap())
        sheet.write(6, 6, "Others (20% of Basic)", reportFormat.table_header_bold_text_wrap())
        sheet.write(6, 7, "Gross", reportFormat.table_header_bold_text_wrap())
        sheet.write(6, 8, "Total Overtime Hour", reportFormat.table_header_bold_text_wrap())
        sheet.write(6, 9, "Overtime Rate/Hour", reportFormat.table_header_bold_text_wrap())
        sheet.write(6, 10, "Total OT Earning Amount", reportFormat.table_header_bold_text_wrap())
        sheet.write(6, 11, "Others/ Arrear", reportFormat.table_header_bold_text_wrap())
        sheet.write(6, 12, "Total", reportFormat.table_header_bold_text_wrap())
        sheet.write(6, 13, "Deduction", reportFormat.table_header_bold_text_wrap())
        sheet.write(6, 14, "Total Payable", reportFormat.table_header_bold_text_wrap())
        return sheet

    def _set_footer_value_n_signature(self, docs, sheet, row, workbook, footer_total_payable):
        reportFormat = ReportFormat(workbook)

        if footer_total_payable > 0:
            amt_to_word = self.env['res.currency'].amount_to_word(float(footer_total_payable))
            row += 3
            sheet.merge_range('A' + str(row + 1) + ':C' + str(row + 1) + '', 'Cash Payment:',
                              reportFormat.text_align_left())
            sheet.merge_range('D' + str(row + 1) + ':E' + str(row + 1) + '', footer_total_payable,
                              reportFormat.text_align_right())
            sheet.merge_range('F' + str(row + 1) + ':M' + str(row + 1) + '', amt_to_word,
                              reportFormat.text_align_left())
            row += 1
            sheet.merge_range('A' + str(row + 1) + ':C' + str(row + 1) + '', 'Total fund Required:',
                              reportFormat.text_align_left())
            sheet.merge_range('D' + str(row + 1) + ':E' + str(row + 1) + '', footer_total_payable,
                              reportFormat.text_align_right())
            sheet.merge_range('F' + str(row + 1) + ':M' + str(row + 1) + '', amt_to_word,
                              reportFormat.text_align_right())

        row += 2
        previous_month_payable = 0
        date_start = datetime.strptime(docs.date_start, "%Y-%m-%d")
        prev_month_start = date_start - relativedelta(months=1)
        hr_payslip_runs = self.env['hr.payslip.run'].search(
            [('date_start', '=', prev_month_start), ('operating_unit_id', '=', docs.operating_unit_id.id),
             ('type', '=', '2')])
        for payslip_run in hr_payslip_runs:
            previous_month_payable += payslip_run.total_payable

        sheet.merge_range('A' + str(row + 1) + ':C' + str(row + 1) + '', 'Previous Month Net Payable was:',
                          reportFormat.text_align_left())
        sheet.merge_range('D' + str(row + 1) + ':E' + str(row + 1) + '', previous_month_payable,
                          reportFormat.text_align_left())

        # Signature
        row += 3
        sheet.write(row, 1, 'Prepared by', reportFormat.text_align_left())
        sheet.write(row, 4, 'Checked by', reportFormat.text_align_left())
        sheet.write(row, 7, 'Recommended by', reportFormat.text_align_left())
        sheet.write(row, 10, 'Authorized by', reportFormat.text_align_left())
        sheet.write(row, 13, 'Approved by', reportFormat.text_align_left())

    def _set_sheet_table_data(self, docs, sheet, workbook):
        reportFormat = ReportFormat(workbook)

        departments = self.env['hr.department'].search([])
        row = 7
        footer_employee = footer_basic = footer_basic_70 = footer_basic_30 = footer_basic_20 = footer_gross = footer_numner_of_hours = 0
        footer_ot_rate = footer_ot_earning_amount = footer_arrear = footer_total = footer_deduction = footer_total_payable = 0

        for department in departments:
            emp_count = ot_earning_amount = 0
            dpt_basic = dpt_basic_70 = dpt_basic_30 = dpt_basic_20 = dpt_gross = dpt_number_of_hours = dpt_ot_rate = ot_arrear = total = deduction = total_payable = 0.0

            payslip_filter_data = list(filter(lambda x: x.employee_id.department_id.id == department.id, docs.slip_ids))
            for slip in payslip_filter_data:
                obj_number_of_hours = list(filter(lambda x: x.code == 'OT', slip.worked_days_line_ids))
                number_of_hours = obj_number_of_hours[0].number_of_hours if obj_number_of_hours else 0
                if number_of_hours > 0:
                    dpt_number_of_hours += number_of_hours
                    emp_count += 1
                    basic = slip.employee_id.contract_id.wage
                    dpt_basic += basic
                    basic_70 = (slip.employee_id.contract_id.wage * 0.70)
                    dpt_basic_70 += basic_70
                    basic_30 = (slip.employee_id.contract_id.wage * 0.30)
                    dpt_basic_30 += basic_30
                    basic_20 = (slip.employee_id.contract_id.wage * 0.20)
                    dpt_basic_20 += basic_20
                    gross = math.ceil((slip.employee_id.contract_id.wage) * 2.5)
                    dpt_gross += gross

                    ot_rate = (basic + basic_70 + basic_30 + basic_30 + basic_20) / 208
                    dpt_ot_rate += ot_rate
                    obj_ot_amount = list(filter(lambda x: x.code == 'EOTA', slip.line_ids))
                    ot_earning_amount += obj_ot_amount[0].amount if obj_ot_amount else 0

                    obj_ot_arrear = list(filter(lambda x: x.code == 'ARSOT', slip.input_line_ids))
                    ot_arrear += obj_ot_arrear[0].amount if obj_ot_arrear else 0

                    total = ot_earning_amount + ot_arrear

                    obj_ot_deduction = list(filter(lambda x: x.code == 'ODSOT', slip.input_line_ids))
                    deduction += obj_ot_deduction[0].amount if obj_ot_deduction else 0

                    obj_total_payable = list(filter(lambda x: x.code == 'NET', slip.line_ids))
                    total_payable += obj_total_payable[0].amount if obj_total_payable else 0

            footer_employee += emp_count
            footer_basic += dpt_basic
            footer_basic_70 += dpt_basic_70
            footer_basic_30 += dpt_basic_30
            footer_basic_20 += dpt_basic_20
            footer_gross += dpt_gross
            footer_numner_of_hours += dpt_number_of_hours
            footer_ot_rate += dpt_ot_rate
            footer_ot_earning_amount += ot_earning_amount
            footer_arrear += ot_arrear
            footer_total += total
            footer_deduction += deduction
            footer_total_payable += total_payable
            if emp_count > 0 and number_of_hours > 0:
                sheet.write(row, 0, department.name, reportFormat.text_align_left_with_border())
                sheet.write(row, 1, emp_count, reportFormat.numeric())
                sheet.write(row, 2, dpt_basic, reportFormat.text_align_right_with_border())
                sheet.write(row, 3, dpt_basic_70, reportFormat.text_align_right_with_border())
                sheet.write(row, 4, dpt_basic_30, reportFormat.text_align_right_with_border())
                sheet.write(row, 5, dpt_basic_30, reportFormat.text_align_right_with_border())
                sheet.write(row, 6, dpt_basic_20, reportFormat.text_align_right_with_border())
                sheet.write(row, 7, dpt_gross, reportFormat.text_align_right_with_border())
                sheet.write(row, 8, dpt_number_of_hours, reportFormat.text_align_right_with_border())
                sheet.write(row, 9, dpt_ot_rate, reportFormat.text_align_right_with_border())
                sheet.write(row, 10, ot_earning_amount, reportFormat.text_align_right_with_border())
                sheet.write(row, 11, ot_arrear, reportFormat.text_align_right_with_border())
                sheet.write(row, 12, total, reportFormat.text_align_right_with_border())
                sheet.write(row, 13, deduction, reportFormat.text_align_right_with_border())
                sheet.write(row, 14, total_payable, reportFormat.text_align_right_with_border())
                row += 1

        # Total
        sheet.write(row, 0, 'Total', reportFormat.text_align_right_bold())
        sheet.write(row, 1, footer_employee, reportFormat.numeric())
        sheet.write(row, 2, footer_basic, reportFormat.text_align_right_bold())
        sheet.write(row, 3, footer_basic_70, reportFormat.text_align_right_bold())
        sheet.write(row, 4, footer_basic_30, reportFormat.text_align_right_bold())
        sheet.write(row, 5, footer_basic_30, reportFormat.text_align_right_bold())
        sheet.write(row, 6, footer_basic_20, reportFormat.text_align_right_bold())
        sheet.write(row, 7, footer_gross, reportFormat.text_align_right_bold())
        sheet.write(row, 8, footer_numner_of_hours, reportFormat.text_align_right_bold())
        sheet.write(row, 9, footer_ot_rate, reportFormat.text_align_right_bold())
        sheet.write(row, 10, footer_ot_earning_amount, reportFormat.text_align_right_bold())
        sheet.write(row, 11, footer_arrear, reportFormat.text_align_right_bold())
        sheet.write(row, 12, footer_total, reportFormat.text_align_right_bold())
        sheet.write(row, 13, footer_deduction, reportFormat.text_align_right_bold())
        sheet.write(row, 14, footer_total_payable, reportFormat.text_align_right_bold())

        return total_payable, row

    def generate_xlsx_report(self, workbook, data, obj):
        docs = obj.hr_payslip_run_id
        sheet = self._get_sheet_header(docs, workbook)

        self._set_sheet_table_header(sheet, workbook)

        total_payable, row = self._set_sheet_table_data(docs, sheet, workbook)

        self._set_footer_value_n_signature(docs, sheet, row, workbook, total_payable)


TopSheetDepartmentXLSX('report.hr_payroll_ot.top_sheet_department_xlsx',
                       'ot.report.wizard', parser=report_sxw.rml_parse)
