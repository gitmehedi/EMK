from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.tools.misc import formatLang
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import math


class MonthlyOtSheetXLSX(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, obj):
        # Report Utility
        ReportUtility = self.env['report.utility']
        hr_payslip_run_id = obj.hr_payslip_run_id
        docs = hr_payslip_run_id
        operating_unit_id = docs.operating_unit_id
        company_id = docs.operating_unit_id.company_id
        report_name = "Monthly OT Report"
        sheet = workbook.add_worksheet(report_name)
        # Then override any that you want.
        sheet.set_row(0, 30)
        sheet.set_row(4, 35)
        sheet.set_column(0, 1, 5)
        sheet.set_column(0, 2, 15)

        # FORMAT
        title_format_center = workbook.add_format({'align': 'center', 'bold': False, 'size': 22, 'text_wrap': True})
        subject_format_center = workbook.add_format({'align': 'center', 'bold': False, 'size': 15, 'text_wrap': True})
        name_format_left_int = workbook.add_format(
            {'align': 'left', 'border': 1, 'bold': False, 'size': 8, 'text_wrap': True})
        bold = workbook.add_format({'bold': True, 'size': 10})
        name_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 8})

        name_border_format_colored = workbook.add_format(
            {'num_format': '#,###0.00','align': 'left', 'border': 1, 'valign': 'vcenter', 'bold': False, 'size': 8})

        name_format_left = workbook.add_format({'align': 'left', 'bold': False, 'size': 10})
        footer_border_format_left = workbook.add_format({'align': 'left', 'bold': True, 'size': 10})

        header_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bg_color': '#FFC000', 'bold': False, 'size': 10, 'border': 1,
             'text_wrap': True})

        sub_header_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bg_color': '#81d41a', 'bold': False, 'size': 10, 'border': 1,
             'text_wrap': True})

        # SHEET HEADER
        sheet.merge_range('A1:R1', company_id.name, title_format_center)
        sheet.merge_range('A2:R2', "Monthly Overtime Sheet", subject_format_center)
        sheet.merge_range('A3:R3', "Operating Unit: " + str(operating_unit_id.name), name_format_left)
        sheet.merge_range('A4:N4', "Overtime Cycle: " + str(docs.date_start) + ' to ' + str(docs.date_end),
                          name_format_left)
        sheet.merge_range('O4:R4', "Initiated by: " + docs.create_date, name_format_left)

        sheet.write(4, 0, "Sl.No.", header_format_left)
        sheet.write(4, 1, "Name", header_format_left)
        sheet.write(4, 2, "Designation", header_format_left)
        sheet.write(4, 3, "Date  of Joining", header_format_left)
        sheet.write(4, 4, "ID No.", header_format_left)
        sheet.write(4, 5, "Basic Salary 40%", header_format_left)
        sheet.write(4, 6, "House Rent 70% of Basic", header_format_left)
        sheet.write(4, 7, "Medical Allowance 30% of Basic", header_format_left)
        sheet.write(4, 8, "Convince Allowance 30% of Basic", header_format_left)
        sheet.write(4, 9, "Other Allowance 20% of Basic", header_format_left)
        sheet.write(4, 10, "Gross", header_format_left)
        sheet.write(4, 11, "Total Overtime Hour", header_format_left)
        sheet.write(4, 12, "Overtime Rate/Hour", header_format_left)
        sheet.write(4, 13, "Total OT Earning Amount", header_format_left)
        sheet.write(4, 14, "Others/ Arrear", header_format_left)
        sheet.write(4, 15, "Total", header_format_left)
        sheet.write(4, 16, "Deduction", header_format_left)
        sheet.write(4, 17, "Net Payable", header_format_left)

        data['name'] = report_name
        dept = self.env['hr.department'].search([])
        dpt_payslips_list = []
        sl = 0
        footer_total_basic_40 = 0
        footer_total_basic_70 = 0
        footer_total_basic_30 = 0
        footer_total_basic_20 = 0
        footer_total_gross = 0
        footer_total_over_time_hours = 0
        footer_total_over_time_rate = 0
        footer_total_ot_earning_amount = 0
        footer_total_arrear = 0
        footer_total_amount = 0
        footer_total_deduction = 0
        footer_total_net_payable = 0

        for d in dept:
            dpt_payslips = {}
            dpt_payslips['name'] = d.name
            dpt_payslips['seq'] = d.sequence
            dpt_payslips['val'] = []

            for slip in docs.slip_ids:
                payslip = {}

                if d.id == slip.employee_id.department_id.id:
                    payslip['emp_name'] = slip.employee_id.name
                    payslip['designation'] = slip.employee_id.job_id.name
                    payslip['doj'] = ReportUtility.get_date_from_string(slip.employee_id.initial_employment_date)

                    gross = math.ceil((slip.employee_id.contract_id.wage) * 2.5)
                    payslip['gross'] = formatLang(self.env, gross)
                    payslip['gross_float'] = gross
                    payslip['emp_id'] = slip.employee_id.barcode
                    payslip['basic_40'] = (slip.employee_id.contract_id.wage * 40) / 100
                    payslip['basic_70'] = (slip.employee_id.contract_id.wage * 70) / 100
                    payslip['basic_30'] = (slip.employee_id.contract_id.wage * 30) / 100
                    payslip['basic_20'] = (slip.employee_id.contract_id.wage * 20) / 100
                    obj_number_of_hours = list(filter(lambda x: x.code == 'OT', slip.worked_days_line_ids))
                    number_of_hours = 0
                    if obj_number_of_hours:
                        number_of_hours = obj_number_of_hours[0].number_of_hours
                    payslip['number_of_hours'] = number_of_hours

                    # OT Rate
                    ot_rate = (slip.employee_id.contract_id.wage + payslip['basic_70'] + payslip['basic_30'] + payslip[
                        'basic_30'] + payslip['basic_20']) / 208
                    payslip['ot_rate_hour'] = ot_rate
                    payslip['ot_earning_amount'] = (number_of_hours * ot_rate)
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

        # Write on excel
        row = 4
        for dpt_emp in dpt_payslips_list:
            print(dpt_emp)
            dpt_val = dpt_emp.get('val')

            if dpt_val:
                row += 1
                dpt_name = dpt_emp.get('name')
                sheet.merge_range('A'+str(row+1)+':R'+str(row+1)+'', dpt_name, sub_header_format_left)

                for emp in dpt_val:
                    row += 1
                    sl += 1
                    sheet.write(row, 0, sl, name_format_left_int)
                    sheet.write(row, 1, emp.get('emp_name'), name_border_format_colored)
                    sheet.write(row, 2, emp.get('designation'), name_border_format_colored)
                    sheet.write(row, 3, emp.get('doj'), name_border_format_colored)
                    sheet.write(row, 4, emp.get('emp_id'), name_border_format_colored)
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
                    footer_total_basic_40 += emp.get('basic_40')
                    footer_total_basic_70 += emp.get('basic_70')
                    footer_total_basic_30 += emp.get('basic_30')
                    footer_total_basic_20 += emp.get('basic_20')
                    footer_total_gross += float(emp.get('gross_float'))
                    footer_total_over_time_hours += emp.get('number_of_hours')
                    footer_total_over_time_rate += emp.get('ot_rate_hour')
                    footer_total_ot_earning_amount += emp.get('ot_earning_amount')
                    footer_total_arrear += emp.get('arrear')
                    footer_total_amount += emp.get('total')
                    footer_total_deduction += emp.get('deduction')
                    footer_total_net_payable += emp.get('total_payable')

        # Footer
        row += 1
        sheet.merge_range('A' + str(row+1) + ':C' + str(row+1) + '', 'Total', footer_border_format_left)
        sheet.write(row, 3, '', footer_border_format_left)
        sheet.write(row, 4, '', footer_border_format_left)
        sheet.write(row, 5, footer_total_basic_40, footer_border_format_left)
        sheet.write(row, 6, footer_total_basic_70, footer_border_format_left)
        sheet.write(row, 7, footer_total_basic_20, footer_border_format_left)
        sheet.write(row, 8, footer_total_basic_30, footer_border_format_left)
        sheet.write(row, 9, footer_total_basic_20, footer_border_format_left)
        sheet.write(row, 10, footer_total_gross, footer_border_format_left)
        sheet.write(row, 11, footer_total_over_time_hours, footer_border_format_left)
        sheet.write(row, 12, footer_total_over_time_rate, footer_border_format_left)
        sheet.write(row, 13, footer_total_ot_earning_amount, footer_border_format_left)
        sheet.write(row, 14, footer_total_arrear, footer_border_format_left)
        sheet.write(row, 15, footer_total_amount, footer_border_format_left)
        sheet.write(row, 16, footer_total_deduction, footer_border_format_left)
        sheet.write(row, 17, footer_total_net_payable, footer_border_format_left)

        # Total Amount
        row += 2
        sheet.write(row, 15, 'Total', footer_border_format_left)
        sheet.write(row, 17, footer_total_net_payable, footer_border_format_left)

        # In Words
        if footer_total_net_payable > 0:
            amt_to_word = self.env['res.currency'].amount_to_word(float(footer_total_net_payable))
            row += 2
            sheet.merge_range('L'+str(row+1)+':R'+str(row+1)+'', 'In Words: ' + amt_to_word, footer_border_format_left)

        # Signature
        row += 3
        sheet.write(row, 1, 'Checked by', name_format_left)
        sheet.write(row, 6, 'Recommended by', name_format_left)
        sheet.write(row, 10, 'Authorized by', name_format_left)
        sheet.write(row, 15, 'Approved by', name_format_left)


        
MonthlyOtSheetXLSX('report.hr_payroll_ot.monthly_ot_sheet_xlsx',
                   'ot.report.wizard', parser=report_sxw.rml_parse)
