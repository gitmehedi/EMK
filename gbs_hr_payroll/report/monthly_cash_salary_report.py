import math
from odoo import api, exceptions, fields, models, tools
from odoo.tools.misc import formatLang


class MonthlyCashSalaryReport(models.AbstractModel):
    _name = 'report.gbs_hr_payroll.report_monthly_cash_salary'

    @api.model
    def render_html(self, docids, data=None):
        payslip_run_pool = self.env['hr.payslip.run']
        docs = payslip_run_pool.browse(docids[0])
        data = {}
        data['name'] = docs.name
        data['type'] = docs.type
        rule_list = []
        for slip in docs.slip_ids:
            if not slip.employee_id.bank_account_id.id:
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
                if not slip.employee_id.bank_account_id.id:
                    if d.id == slip.employee_id.department_id.id:
                        payslip['emp_name'] = slip.employee_id.name
                        payslip['designation'] = slip.employee_id.job_id.name
                        payslip['doj'] = slip.employee_id.initial_employment_date
                        payslip['emp_seq'] = slip.employee_id.employee_sequence
                        loan_remain = slip.remaining_loan or 0.00
                        payslip['loan_balance'] = formatLang(self.env, loan_remain) if loan_remain else None
                        payslip['sa'] = formatLang(self.env,
                                                   math.ceil(slip.employee_id.contract_id.supplementary_allowance))
                        gross = math.ceil((slip.employee_id.contract_id.wage) * 2.5)
                        payslip['gross'] = formatLang(self.env, gross)

                        for rule in rule_list:
                            payslip[rule['code']] = 0

                            for line in slip.line_ids:
                                if line.code == rule['code']:
                                    total_amount = math.ceil(line.total)
                                    payslip[rule['code']] = formatLang(self.env, total_amount)

                                    row_total[line.code] = row_total[line.code] + (math.ceil(total_amount))

                                    if line.code == "NET":
                                        total_sum.append(math.ceil(total_amount))

                                    break;

                        dpt_payslips['val'].append(payslip)

            emp_sort_list = dpt_payslips['val']
            emp_sort_list = sorted(emp_sort_list, key=lambda k: k['emp_seq'])

            for ps in emp_sort_list:
                ps['sn'] = sn
                sn += 1

            dpt_payslips['val'] = emp_sort_list
            dpt_payslips_list.append(dpt_payslips)


        all_total = sum(total_sum)

        dpt_payslips_list.append(dpt_payslips)
        amt_to_word = self.env['res.currency'].amount_to_word(float(all_total))

        # locale.setlocale(locale.LC_ALL, 'bn_BD.UTF-8')
        # thousand_separated_total_sum = locale.currency(all_total, grouping=True)

        thousand_separated_total_sum = formatLang(self.env, all_total)

        for rule in rule_list:
            row_total[rule['code']] = formatLang(self.env, row_total[rule['code']])

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'hr.payslip.run',
            'docs': dpt_payslips_list,
            'docs_len': len(rule_list) + 8,
            'rules': rule_list,
            'total_sum': thousand_separated_total_sum,
            'amt_to_word': amt_to_word,
            'data': data,
            'row_total': row_total,
        }

        return self.env['report'].render('gbs_hr_payroll.report_monthly_cash_salary', docargs)