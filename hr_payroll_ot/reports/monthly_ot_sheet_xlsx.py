from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.tools.misc import formatLang
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
        # sheet.set_column(0, 1, 26)
        for col in range(50):
            sheet.set_column(col, col, 20)

        # Then override any that you want.
        sheet.set_column(0, 0, 5)

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
        header_name_format_left = workbook.add_format(
            {'align': 'left', 'bold': True, 'size': 8, 'bg_color': '#4C0099', 'font_color': 'white'})
        header_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bg_color': '#d7ecfa', 'bold': True, 'size': 8, 'border': 1,
             'text_wrap': True})

        # SHEET HEADER
        sheet.merge_range('A1:O1', company_id.name, name_format_left)
        sheet.merge_range('A2:O2', "Operating Unit: " + str(operating_unit_id.name), name_format_left)
        sheet.merge_range('A3:O3', "Overtime Cycle: " + str(docs.date_start) + ' to ' + str(docs.date_end),
                          name_format_left)
        sheet.merge_range('A4:O4', "Report Name: Monthly OT Report", name_format_left)

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
        sheet.write(5, 17, "Total Payable", header_format_left)
        sheet.write(5, 18, "Remarks", header_format_left)

        data['name'] = report_name

        data = {}
        data['name'] = docs.name
        data['type'] = docs.type
        rule_list = []
        for slip in docs.slip_ids:
            for line in slip.line_ids:
                if line.appears_on_payslip is True:
                    rule = {}
                    rule['name'] = line.name
                    rule['seq'] = line.sequence
                    rule['code'] = line.code

                    if rule not in rule_list:
                        rule_list.append(rule)

        rule_list = sorted(rule_list, key=lambda k: k['seq'])

        dept = self.env['hr.department'].search([])

        dpt_payslips_list = []
        total_sum = []
        sn = 1

        row_total = {}
        for srule in rule_list:
            row_total[srule['code']] = 0

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
                    payslip['emp_seq'] = slip.employee_id.employee_sequence
                    loan_remain = slip.remaining_loan or 0.00
                    payslip['loan_balance'] = formatLang(self.env, loan_remain) if loan_remain else None
                    payslip['sa'] = formatLang(self.env,
                                               math.ceil(slip.employee_id.contract_id.supplementary_allowance))
                    gross = math.ceil((slip.employee_id.contract_id.wage) * 2.5)
                    payslip['gross'] = formatLang(self.env, gross)
                    payslip['emp_id'] = slip.employee_id.barcode
                    payslip['basic_40'] = (slip.employee_id.contract_id.wage * 40) / 100
                    payslip['basic_70'] = (slip.employee_id.contract_id.wage * 70) / 100
                    payslip['basic_30'] = (slip.employee_id.contract_id.wage * 30) / 100
                    payslip['basic_20'] = (slip.employee_id.contract_id.wage * 20) / 100
                    # payslip['number_of_hours'] = slip.worked_days_line_ids.search([('code', '=', 'OT')])
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
                    arrear = 0
                    payslip['arrear'] = arrear
                    payslip['total'] = payslip['ot_earning_amount'] + payslip['arrear']

                    deduction = 0
                    payslip['deduction'] = deduction
                    payslip['total_payable'] = payslip['total'] - payslip['deduction']

                    for rule in rule_list:
                        payslip[rule['code']] = 0

                        for line in slip.line_ids:
                            if line.code == rule['code']:
                                total_amount = math.ceil(line.total)
                                payslip[rule['code']] = formatLang(self.env, total_amount)

                                row_total[line.code] = row_total[line.code] + (math.ceil(total_amount))

                                if line.code == "NET":
                                    total_sum.append(math.ceil(total_amount))

                                break

                    dpt_payslips['val'].append(payslip)

            emp_sort_list = dpt_payslips['val']
            emp_sort_list = sorted(emp_sort_list, key=lambda k: k['emp_seq'])

            for ps in emp_sort_list:
                ps['sn'] = sn
                sn += 1

            dpt_payslips['val'] = emp_sort_list
            dpt_payslips_list.append(dpt_payslips)

        # Write on excel
        row = 5
        for dpt_emp in dpt_payslips_list:
            print(dpt_emp)
            dpt_val = dpt_emp.get('val')

            if dpt_val:
                dpt_name = dpt_emp.get('name')
                # sheet.merge_range('A'+str(row)+':O'+str(row)+'', dpt_name, header_name_format_left)
                sheet.merge_range('A'+str(row)+':S'+str(row)+'', dpt_name, header_name_format_left)

                # sheet.write(row, 0, dpt_name, name_border_format_colored)

                for emp in dpt_val:
                    row += 1
                    sheet.write(row, 0, row - 6, name_border_format_colored)
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
                    sheet.write(row, 18, '', name_border_format_colored)


MonthlyOtSheetXLSX('report.hr_payroll_ot.monthly_ot_sheet_xlsx',
                   'ot.report.wizard', parser=report_sxw.rml_parse)
