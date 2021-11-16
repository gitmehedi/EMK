from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.tools.misc import formatLang
from odoo.tools import float_compare, float_round
from collections import OrderedDict
import operator, math, locale


class CostCenterWiseTopSheetXLSX(ReportXlsx):

    def get_payslip_list(self, cost_center, top_sheet):
        self.env.cr.execute("""
                            select id from hr_payslip where employee_id in 
                            (select id from hr_employee where cost_center_id = %s) 
                            and payslip_run_id = %s
                        """ % (cost_center.id, top_sheet.id))
        payslip_list = []
        for id in self.env.cr.fetchall():
            payslip_list.append(self.env['hr.payslip'].browse(id))
        return payslip_list

    def get_rule_list(self, payslip_list):
        rule_list = []

        for slip in payslip_list:
            for line in slip.line_ids:
                if (line.sequence, line.name) not in rule_list and line.appears_on_payslip:
                    rule_list.append((line.sequence, line.name))

        rule_list = sorted(rule_list, key=lambda k: k[0])
        return rule_list

    def get_final_rule_list(self, all_rule_list, final_rule_list):
        lst3 = [value for value in final_rule_list if value in all_rule_list]
        return lst3

    def generate_xlsx_report(self, workbook, data, obj):

        report_name = 'Cost Center Wise Top Sheet'
        sheet = workbook.add_worksheet(report_name)
        bold = workbook.add_format({'font_size': 8, 'bold': True})
        header_bold = workbook.add_format({'font_size': 8, 'bold': True, 'border': 1})
        bg_bold = workbook.add_format({'font_size': 8, 'bold': True, 'bg_color': '#78B0DE'})
        normal = workbook.add_format({'font_size': 8})
        bg_normal = workbook.add_format({'font_size': 8, 'bg_color': '#78B0DE'})
        bg_normal_bordered = workbook.add_format({'font_size': 8, 'bg_color': '#78B0DE', 'border': 1})
        # .add_format({'bg_color': '#00C7CE'})
        top_sheet = obj.hr_payslip_run_id
        header_created = 0
        last_row = 0
        rule_list_created = 0
        final_rule_list = []

        all_rule_list = []
        for rule in self.env['hr.salary.rule'].search([], order="sequence"):
            all_rule_list.append((rule.sequence, rule.name))
        all_rule_list = sorted(all_rule_list, key=lambda k: k[0])
        grand_total = OrderedDict()
        for rule in all_rule_list:
            grand_total[rule[1]] = 0

        total_employee_count = 0
        if obj.cost_center_ids:
            for cost_center in obj.cost_center_ids:
                payslip_list = self.get_payslip_list(cost_center, top_sheet)
                if not payslip_list:
                    continue
                rule_list = self.get_rule_list(payslip_list)

                if rule_list:
                    rule_list_created = rule_list_created + 1
                    if rule_list_created == 1:
                        final_rule_list = rule_list
                    elif rule_list_created > 1:
                        if len(rule_list) > len(final_rule_list):
                            diff = list(set(rule_list) - set(final_rule_list)) + list(
                                set(final_rule_list) - set(rule_list))

                            for val in diff:
                                final_rule_list.append(val)

                        elif len(final_rule_list) > len(rule_list):
                            diff = list(set(final_rule_list) - set(rule_list)) + list(
                                set(rule_list) - set(final_rule_list))
                            for val in diff:
                                final_rule_list.append(val)

            final_rule_list = list(dict.fromkeys(final_rule_list))
            final_rule_list = sorted(final_rule_list, key=lambda k: k[0])
            final_rule_list = self.get_final_rule_list(all_rule_list, final_rule_list)

            print('final_rule_list')

            for cost_center in obj.cost_center_ids:
                payslip_list = self.get_payslip_list(cost_center, top_sheet)
                if not payslip_list:
                    continue

                header = OrderedDict()
                header[0] = 'Cost Center'
                header[1] = 'Department'
                header[2] = 'Employee'
                for rec in final_rule_list:
                    print('rec', rec)
                    header[len(header)] = rec[1]
                for key, value in header.items():
                    sheet.write(0, key, value, header_bold)
                header_created = header_created + 1

                record = OrderedDict()
                for rec in payslip_list:
                    rules = OrderedDict()
                    for rule in final_rule_list:
                        rules[rule[1]] = 0
                    record[rec.employee_id.department_id.name] = {}
                    record[rec.employee_id.department_id.name]['count'] = 0
                    record[rec.employee_id.department_id.name]['vals'] = rules

                total = OrderedDict()
                for rule in final_rule_list:
                    total[rule[1]] = 0

                bnet = 0
                net = 0

                for slip in payslip_list:
                    rec = record[slip.employee_id.department_id.name]
                    rec['count'] = rec['count'] + 1
                    for line in slip.line_ids:
                        if line.appears_on_payslip:
                            rec['vals'][line.name] = rec['vals'][line.name] + math.ceil(line.total)
                            total[line.name] = total[line.name] + math.ceil(line.total)
                        if line.code == 'BNET' and slip.employee_id.bank_account_id.bank_id:
                            bnet = bnet + math.ceil(line.total)
                        if line.code == 'NET':
                            net = net + math.ceil(line.total)

                sheet.write(last_row + 1, 0, cost_center.name, normal)

                row = last_row + 1 + 1
                sub_employee_count = 0
                for key, value in record.items():
                    sheet.write(row, 1, key, normal)
                    sheet.write(row, 2, value['count'], normal)
                    col = 3
                    for rule_key, rule_value in value['vals'].items():
                        sheet.write(row, col, rule_value, normal)
                        col = col + 1
                    row = row + 1
                    sub_employee_count = sub_employee_count + value['count']

                sheet.write(row, 0, 'Sub Total', bg_normal_bordered)
                sheet.write(row, 1, ' ', bg_normal_bordered)
                sheet.write(row, 2, sub_employee_count, bg_normal_bordered)
                total_employee_count = total_employee_count + sub_employee_count

                set1 = set(total)
                set2 = set(grand_total)
                shared_items = set2 - set1

                for name in shared_items:
                    if name in grand_total:
                        del grand_total[name]
                total_col = 3
                for key, value in total.items():
                    sheet.write(row, total_col, value, bg_normal_bordered)
                    grand_total[key] = grand_total[key] + value
                    total_col = total_col + 1
                last_row = row
        else:
            cost_centers = self.env['account.cost.center'].search([])

            for cost_center in cost_centers:
                payslip_list = self.get_payslip_list(cost_center, top_sheet)
                if not payslip_list:
                    continue
                rule_list = self.get_rule_list(payslip_list)

                if rule_list:
                    rule_list_created = rule_list_created + 1
                    if rule_list_created == 1:
                        final_rule_list = rule_list
                    elif rule_list_created > 1:
                        if len(rule_list) > len(final_rule_list):
                            diff = list(set(rule_list) - set(final_rule_list)) + list(
                                set(final_rule_list) - set(rule_list))

                            for val in diff:
                                final_rule_list.append(val)

                        elif len(final_rule_list) > len(rule_list):
                            diff = list(set(final_rule_list) - set(rule_list)) + list(
                                set(rule_list) - set(final_rule_list))
                            for val in diff:
                                final_rule_list.append(val)

            final_rule_list = list(dict.fromkeys(final_rule_list))
            final_rule_list = sorted(final_rule_list, key=lambda k: k[0])
            final_rule_list = self.get_final_rule_list(all_rule_list, final_rule_list)

            for cost_center in cost_centers:
                payslip_list = self.get_payslip_list(cost_center, top_sheet)
                if not payslip_list:
                    continue
                header = OrderedDict()
                header[0] = 'Cost Center'
                header[1] = 'Department'
                header[2] = 'Employee'
                for rec in final_rule_list:
                    print('rec', rec)
                    header[len(header)] = rec[1]
                for key, value in header.items():
                    # sheet.set_column(0, 12, 16)
                    sheet.write(0, key, value, header_bold)
                header_created = header_created + 1

                record = OrderedDict()
                for rec in payslip_list:
                    rules = OrderedDict()
                    for rule in final_rule_list:
                        rules[rule[1]] = 0
                    record[rec.employee_id.department_id.name] = {}
                    record[rec.employee_id.department_id.name]['count'] = 0
                    record[rec.employee_id.department_id.name]['vals'] = rules

                total = OrderedDict()
                for rule in final_rule_list:
                    total[rule[1]] = 0

                bnet = 0
                net = 0

                for slip in payslip_list:
                    rec = record[slip.employee_id.department_id.name]
                    rec['count'] = rec['count'] + 1
                    for line in slip.line_ids:
                        if line.appears_on_payslip:
                            rec['vals'][line.name] = rec['vals'][line.name] + math.ceil(line.total)
                            total[line.name] = total[line.name] + math.ceil(line.total)
                        if line.code == 'BNET' and slip.employee_id.bank_account_id.bank_id:
                            bnet = bnet + math.ceil(line.total)
                        if line.code == 'NET':
                            net = net + math.ceil(line.total)

                sheet.write(last_row + 1, 0, cost_center.name, normal)

                row = last_row + 1 + 1
                sub_employee_count = 0
                for key, value in record.items():
                    sheet.write(row, 1, key, normal)
                    sheet.write(row, 2, value['count'], normal)
                    col = 3
                    for rule_key, rule_value in value['vals'].items():
                        sheet.write(row, col, rule_value, normal)
                        col = col + 1
                    row = row + 1
                    sub_employee_count = sub_employee_count + value['count']

                sheet.write(row, 0, 'Sub Total', bg_normal_bordered)
                sheet.write(row, 1, ' ', bg_normal_bordered)
                sheet.write(row, 2, sub_employee_count, bg_normal_bordered)
                total_employee_count = total_employee_count + sub_employee_count

                set1 = set(total)
                set2 = set(grand_total)
                shared_items = set2 - set1

                for name in shared_items:
                    if name in grand_total:
                        del grand_total[name]

                # print('shared items', shared_items)
                print('total dict', total)
                total_col = 3
                for key, value in total.items():
                    sheet.write(row, total_col, value, bg_normal_bordered)
                    grand_total[key] = grand_total[key] + value
                    total_col = total_col + 1
                last_row = row
        sheet.write(last_row + 1, 0, 'Total', bg_normal_bordered)
        sheet.write(last_row + 1, 1, ' ', bg_normal_bordered)
        sheet.write(last_row + 1, 2, total_employee_count, bg_normal_bordered)

        grand_total_col = 3
        for key, value in grand_total.items():
            sheet.write(last_row + 1, grand_total_col, value, bg_normal_bordered)
            grand_total_col = grand_total_col + 1

        data['name'] = top_sheet.name


CostCenterWiseTopSheetXLSX('report.gbs_hr_payroll_costcenter_wise_top_sheet.cost_center_wise_top_sheet_xlsx',
                           'cost.center.top.sheet.wizard', parser=report_sxw.rml_parse)
