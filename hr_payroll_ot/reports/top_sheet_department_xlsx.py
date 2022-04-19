from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from datetime import datetime


class TopSheetDepartmentXLSX(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, obj):
        # Report Utility
        ReportUtility = self.env['report.utility']
        hr_payslip_run_id = obj.hr_payslip_run_id
        docs = hr_payslip_run_id
        operating_unit_id = docs.operating_unit_id
        company_id = docs.operating_unit_id.company_id
        report_name = "Top Sheet (Department)"
        sheet = workbook.add_worksheet(report_name)
        # sheet.set_column(0, 1, 26)
        for col in range(50):
            sheet.set_column(col, col, 25)
        sheet.set_row(4, 25)

        # Then override any that you want.
        name_format_left = workbook.add_format({'align': 'left', 'bold': True, 'size': 8})
        header_name_format_left = workbook.add_format(
            {'align': 'left', 'bold': True, 'size': 8, 'bg_color': '#4C0099', 'font_color': 'white'})
        header_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bg_color': '#d7ecfa', 'bold': True, 'size': 8, 'border': 1,
             'text_wrap': True})
        name_border_format_colored = workbook.add_format(
            {'align': 'center', 'border': 1, 'bg_color': '#eaede6', 'valign': 'vcenter', 'bold': True, 'size': 8})
        # SHEET HEADER
        sheet.merge_range('A1:P1', str(docs.date_start), name_format_left)
        sheet.merge_range('A2:P2', "Initiated by : Human Resources", name_format_left )
        sheet.merge_range('A3:P3', "To : Managing Director",name_format_left)
        sheet.merge_range('A4:P4', "Money Requisition for Disbursement of Overtime : SCCL-DF February 2022", name_format_left)

        sheet.write(4, 0, "Department", header_format_left)
        sheet.write(4, 1, "Employee", header_format_left)
        sheet.write(4, 2, "Basic", header_format_left)
        sheet.write(4, 3, "House Rent Allowance (70% of Basic)", header_format_left)
        sheet.write(4, 4, "Medical Allowance (30% of Basic)", header_format_left)
        sheet.write(4, 5, "Conveyance Allowance (30% of Basic)", header_format_left)
        sheet.write(4, 6, "Others (20% of Basic)", header_format_left)
        sheet.write(4, 7, "Gross", header_format_left)
        sheet.write(4, 8, "Total Overtime Hour", header_format_left)
        sheet.write(4, 9, "Overtime Rate/Hour", header_format_left)
        sheet.write(4, 10, "Total OT Earning Amount", header_format_left)
        sheet.write(4, 11, "Others/ Arrear", header_format_left)
        sheet.write(4, 12, "Total", header_format_left)
        sheet.write(4, 13, "Deduction", header_format_left)
        sheet.write(4, 14, "Total Payable", header_format_left)
        sheet.write(4, 15, "Remarks", header_format_left)
        data['name'] = report_name



TopSheetDepartmentXLSX('report.hr_payroll_ot.top_sheet_department_xlsx',
                   'ot.report.wizard', parser=report_sxw.rml_parse)