from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.tools.misc import formatLang
from dateutil.relativedelta import relativedelta
from datetime import datetime
import math

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
        sheet.set_row(0, 30)
        sheet.set_row(5, 30)
        sheet.set_column(0, 0, 22)
        # sheet.set_default_row(22)

        # Then override any that you want.

        title_format_center = workbook.add_format({'align': 'center', 'bold': True, 'size': 22, 'text_wrap': True})
        subject_format_center = workbook.add_format({'align': 'center', 'bold': True, 'size': 10, 'text_wrap': True})
        name_format_left = workbook.add_format({'num_format': '#,##0.00','align': 'left', 'bold': False, 'size': 8, 'text_wrap': True})
        name_format_left_int = workbook.add_format({'align': 'left', 'border': 1, 'bold': False, 'size': 8, 'text_wrap': True})
        footer_name_format_left = workbook.add_format(
            {'align': 'left', 'border': 1, 'bold': True, 'size': 8, 'font_color': 'black'})
        header_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bg_color': '#FFC000', 'bold': False, 'size': 8, 'border': 1,
             'text_wrap': True})
        name_border_format_colored = workbook.add_format(
            {'num_format': '#,###0.00','align': 'center', 'border': 1,  'valign': 'vcenter', 'bold': False, 'size': 8})
        # SHEET HEADER
        sheet.merge_range('A1:O1', company_id.name, title_format_center)
        sheet.merge_range('A2:O2', str(docs.date_start), name_format_left)
        sheet.merge_range('A3:O3', "Initiated by : Human Resources", name_format_left)
        sheet.merge_range('A4:O4', "To : Managing Director", name_format_left)
        sheet.merge_range('A5:O5', "Money Requisition for Disbursement of Overtime : " + docs.name + "", subject_format_center)

        sheet.write(5, 0, "Department", header_format_left)
        sheet.write(5, 1, "No of Employee", header_format_left)
        sheet.write(5, 2, "Basic", header_format_left)
        sheet.write(5, 3, "House Rent Allowance (70% of Basic)", header_format_left)
        sheet.write(5, 4, "Medical Allowance (30% of Basic)", header_format_left)
        sheet.write(5, 5, "Conveyance Allowance (30% of Basic)", header_format_left)
        sheet.write(5, 6, "Others (20% of Basic)", header_format_left)
        sheet.write(5, 7, "Gross", header_format_left)
        sheet.write(5, 8, "Total Overtime Hour", header_format_left)
        sheet.write(5, 9, "Overtime Rate/Hour", header_format_left)
        sheet.write(5, 10, "Total OT Earning Amount", header_format_left)
        sheet.write(5, 11, "Others/ Arrear", header_format_left)
        sheet.write(5, 12, "Total", header_format_left)
        sheet.write(5, 13, "Deduction", header_format_left)
        sheet.write(5, 14, "Total Payable", header_format_left)
        data['name'] = report_name

        dept = self.env['hr.department'].search([])
        row = 6
        footer_employee = 0
        footer_basic = 0
        footer_basic_70 = 0
        footer_basic_30 = 0
        footer_basic_20 = 0
        footer_gross = 0
        footer_numner_of_hours = 0
        footer_ot_rate = 0
        footer_ot_amount = 0
        footer_ot_earning_amount = 0
        footer_arrear = 0
        footer_total = 0
        footer_deduction = 0
        footer_total_payable = 0

        for d in dept:
            emp_count = 0
            basic = 0
            basic_70 = 0
            basic_30 = 0
            basic_20 = 0
            gross = 0
            number_of_hours = 0
            ot_rate = 0
            ot_earning_amount = 0
            ot_arrear = 0
            total = 0
            deduction = 0
            total_payable = 0


            for slip in docs.slip_ids:
                if d.id == slip.employee_id.department_id.id:
                    emp_count += 1
                    basic += slip.employee_id.contract_id.wage
                    basic_70 += (slip.employee_id.contract_id.wage * 70) / 100
                    basic_30 += (slip.employee_id.contract_id.wage * 30) / 100
                    basic_20 += (slip.employee_id.contract_id.wage * 20) / 100
                    gross += math.ceil((slip.employee_id.contract_id.wage) * 2.5)
                    obj_number_of_hours = list(filter(lambda x: x.code == 'OT', slip.worked_days_line_ids))
                    if obj_number_of_hours:
                        number_of_hours += obj_number_of_hours[0].number_of_hours
                    ot_rate += (basic + basic_70 + basic_30 + basic_30 + basic_20)/208
                    ot_earning_amount += (number_of_hours * ot_rate)
                    ot_arrear += 0
                    total += ot_earning_amount + ot_arrear
                    deduction += 0
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
            if emp_count > 0:
                sheet.write(row, 0, d.name, name_border_format_colored)
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

        amt_to_word = self.env['res.currency'].amount_to_word(float(footer_total_payable))
        # Total
        sheet.write(row, 0, 'Total', name_format_left)
        sheet.write(row, 1, footer_employee, footer_name_format_left)
        sheet.write(row, 2, footer_basic, footer_name_format_left)
        sheet.write(row, 3, footer_basic_70, footer_name_format_left)
        sheet.write(row, 4, footer_basic_30, footer_name_format_left)
        sheet.write(row, 5, footer_basic_30, footer_name_format_left)
        sheet.write(row, 6, footer_basic_20, footer_name_format_left)
        sheet.write(row, 7, footer_gross, footer_name_format_left)
        sheet.write(row, 8, footer_numner_of_hours, footer_name_format_left)
        sheet.write(row, 9, footer_ot_rate, footer_name_format_left)
        sheet.write(row, 10, footer_ot_earning_amount, footer_name_format_left)
        sheet.write(row, 11, footer_arrear, footer_name_format_left)
        sheet.write(row, 12, footer_total, footer_name_format_left)
        sheet.write(row, 13, footer_deduction, footer_name_format_left)
        sheet.write(row, 14, footer_total_payable, footer_name_format_left)

        # Previous month payable value
        previous_month_payable = 0
        date_start = datetime.strptime(docs.date_start, "%Y-%m-%d")
        prev_month_start = date_start - relativedelta(months=1)
        hr_payslip_runs = self.env['hr.payslip.run'].search([('date_start', '=', prev_month_start), ('operating_unit_id', '=', operating_unit_id.id)])
        for hr_payslip_run in hr_payslip_runs:
            basic=0
            basic_70=0
            basic_30=0
            basic_20=0
            number_of_hours=0
            ot_rate=0
            ot_earning_amount=0
            ot_arrear=0
            total=0
            deduction = 0
            for slip in hr_payslip_run.slip_ids:
                basic += slip.employee_id.contract_id.wage
                # basic_70 += (slip.employee_id.contract_id.wage * 70) / 100
                # basic_30 += (slip.employee_id.contract_id.wage * 30) / 100
                # basic_20 += (slip.employee_id.contract_id.wage * 20) / 100
                # obj_number_of_hours = list(filter(lambda x: x.code == 'OT', slip.worked_days_line_ids))
                # if obj_number_of_hours:
                #     number_of_hours += obj_number_of_hours[0].number_of_hours
                # ot_rate += (basic + basic_70 + basic_30 + basic_30 + basic_20) / 208
                # ot_earning_amount += (number_of_hours * ot_rate)
                # ot_arrear += 0
                # total += ot_earning_amount + ot_arrear
                # deduction += 0
            previous_month_payable += basic
        prev_amt_to_word = self.env['res.currency'].amount_to_word(float(previous_month_payable))

        row += 3
        sheet.write(row, 0, 'Cash Payment:', name_format_left)
        sheet.write(row, 1, footer_total_payable, name_format_left)
        sheet.merge_range('C'+str(row+1)+':H'+str(row+1)+'', amt_to_word, name_format_left)
        row += 1
        sheet.write(row, 0, 'Total fund Required:', name_format_left)
        sheet.write(row, 1, footer_total_payable, name_format_left)
        sheet.merge_range('C'+str(row+1)+':H'+str(row+1)+'', amt_to_word, name_format_left)
        # sheet.write(row, 2, amt_to_word, name_format_left)
        row += 2
        sheet.write(row, 0, 'Previous Month Net Payable was:', name_format_left)
        sheet.write(row, 1, footer_total_payable, name_format_left)
        sheet.merge_range('C' + str(row + 1) + ':H' + str(row + 1) + '', prev_amt_to_word, name_format_left)
        # Signature
        row += 3
        sheet.write(row, 0, 'Prepared by', name_format_left)
        sheet.write(row, 2, 'Checked by', name_format_left)
        sheet.merge_range('F'+str(row+1)+':G'+str(row+1)+'', 'Recommended by', name_format_left)
        sheet.merge_range('J'+str(row+1)+':K'+str(row+1)+'', 'Authorized by', name_format_left)
        sheet.write(row, 13, 'Approved by', name_format_left)

TopSheetDepartmentXLSX('report.hr_payroll_ot.top_sheet_department_xlsx',
                   'ot.report.wizard', parser=report_sxw.rml_parse)