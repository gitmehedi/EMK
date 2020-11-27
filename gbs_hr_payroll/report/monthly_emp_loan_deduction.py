import decimal, math
from odoo import api, exceptions, fields, models, tools
from odoo.tools.misc import formatLang


class MonthlyLoanDeduction(models.AbstractModel):
    _name = 'report.gbs_hr_payroll.report_monthly_loan_deduction'

    @api.model
    def render_html(self, docids, data=None):
        payslip_run_pool = self.env['hr.payslip.run']
        docs = payslip_run_pool.browse(data.get('active_id'))
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
                    payslip['department'] = slip.employee_id.department_id.name
                    payslip['doj'] = slip.employee_id.initial_employment_date
                    payslip['device_employee_acc'] = slip.employee_id.device_employee_acc
                    payslip['emp_seq'] = slip.employee_id.employee_sequence
                    payslip['initial_loan'] = slip.remaining_loan
                    payslip['remain_loan'] = 0.00

                    for rule in rule_list:
                        payslip[rule['code']] = 0
                        for line in slip.line_ids:
                            if line.code == rule['code']:
                                total_amount = abs(math.ceil(line.total))
                                payslip[rule['code']] = total_amount
                                row_total[line.code] = row_total[line.code] + (math.ceil(total_amount))

                    dpt_payslips['val'].append(payslip)
            emp_sort_list = dpt_payslips['val']
            emp_sort_list = sorted(emp_sort_list, key=lambda k: k['emp_seq'])
            for ps in emp_sort_list:
                ps['sn'] = sn
                sn += 1
            dpt_payslips['val'] = emp_sort_list
            dpt_payslips_list.append(dpt_payslips)
        loan_val = []
        for rec in dpt_payslips_list:
            if rec['val']:
                for value in rec['val']:
                    if value['LOAN'] != 0:
                        initial_loan = float(value['initial_loan'])
                        value['initial_loan'] = formatLang(self.env, initial_loan)
                        loan_amt = float(value['LOAN'])
                        value['LOAN'] = formatLang(self.env, loan_amt)
                        value['remain_loan'] = formatLang(self.env, (initial_loan - loan_amt))
                        loan_val.append(value)

        for rule in rule_list:
            row_total[rule['code']] = formatLang(self.env, row_total[rule['code']])

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'hr.payslip.run',
            'docs': dpt_payslips_list,
            'loan_list': loan_val,
            'docs_len': len(rule_list) + 8,
            'rules': rule_list,
            'data': data,
            'row_total': row_total,
        }

        return self.env['report'].render('gbs_hr_payroll.report_monthly_loan_deduction', docargs)
