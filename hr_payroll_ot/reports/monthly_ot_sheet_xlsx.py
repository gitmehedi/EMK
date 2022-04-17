from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.tools.misc import formatLang
import math


class MonthlyOtSheetXLSX(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, obj):
        ReportUtility = self.env['report.utility']
        hr_payslip_run_id = obj.hr_payslip_run_id
        docs = hr_payslip_run_id
        operating_unit_id = docs.operating_unit_id
        company_id = docs.operating_unit_id.company_id
        report_name = "Monthly OT Report"
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
            {'num_format': '#,###0.00', 'align': 'left', 'size': 8})
        name_format_left = workbook.add_format({'align': 'left', 'bold': True, 'size': 8})
        header_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bg_color': '#d7ecfa', 'bold': True, 'size': 8, 'border': 1})

        address_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 7})

        # SHEET HEADER
        sheet.merge_range('A1:O1', company_id.name, name_format_left)
        sheet.merge_range('A2:O2', "Operating Unit: " + str(operating_unit_id.name), name_format_left)
        sheet.merge_range('A3:O3', "Overtime Cycle: " + str(docs.date_start) + ' to ' + str(docs.date_end), name_format_left)
        sheet.merge_range('A4:O4', "Report Name: Monthly OT Report", name_format_left)

        sheet.write(5, 0, "Sl.No.", header_format_left)
        sheet.write(5, 1, "Name", header_format_left)
        sheet.write(5, 2, "Designation", header_format_left)
        sheet.write(5, 3, "ID No.", header_format_left)
        sheet.write(5, 4, "Basic Salary 40%", header_format_left)
        sheet.write(5, 5, "House Rent 70% of Basic", header_format_left)
        sheet.write(5, 6, "Medical Allowance 30% of Basic", header_format_left)
        sheet.write(5, 7, "Convince Allowance 30% of Basic", header_format_left)
        sheet.write(5, 8, "Other Allowance 20% of Basic", header_format_left)
        sheet.write(5, 9, "Gross", header_format_left)
        sheet.write(5, 10, "Total Overtime Hour", header_format_left)
        sheet.write(5, 11, "Overtime Rate/Hour", header_format_left)
        sheet.write(5, 12, "Total OT Earning Amount", header_format_left)
        sheet.write(5, 13, "Others/ Arrear", header_format_left)
        sheet.write(5, 14, "Total", header_format_left)
        sheet.write(5, 15, "Deduction", header_format_left)
        sheet.write(5, 16, "Total Payable", header_format_left)
        sheet.write(5, 17, "Remarks", header_format_left)

        data['name'] = report_name



MonthlyOtSheetXLSX('report.hr_payroll_ot.monthly_ot_sheet_xlsx',
                       'ot.report.wizard', parser=report_sxw.rml_parse)
