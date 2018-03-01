from odoo import api, exceptions, fields, models
import operator, math
import locale


class PayrollReportPivotal(models.AbstractModel):
    _name = 'report.gbs_hr_payroll.report_individual_payslip'

    @api.model
    def render_html(self, docids, data=None):
        payslip_run_pool = self.env['hr.payslip.run']
        docs = payslip_run_pool.browse(docids[0])
        data = {}
        data['name'] = docs.name
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
        gross_total_sum = []
        salary_deduction_sum = []
        mess_deduction_sum = []
        loan_deduction_sum = []
        arrear_allowance_sum = []
        other_allowance_sum = []
        mobile_allowance_sum = []
        special_allowance = []
        pf_contribution_sum = []

        sn = 1

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
                    payslip['doj'] = slip.employee_id.initial_employment_date
                    payslip['emp_seq'] = slip.employee_id.employee_sequence
                    loan_remain = slip.remaining_loan or 0.00
                    payslip['loan_balance'] = format(loan_remain, '.2f') if loan_remain else None

                    for rule in rule_list:
                        payslip[rule['code']] = 0
                        for line in slip.line_ids:
                            if line.code == rule['code']:
                                total_amount = math.ceil(line.total)
                                payslip[rule['code']] = total_amount

                                if line.code == 'GROSS':
                                    gross_total_sum.append(math.ceil(total_amount))

                                if line.code == 'ABS':  # Salary Deduction
                                    salary_deduction_sum.append(math.ceil(total_amount))

                                if line.code == 'MESS':
                                    mess_deduction_sum.append(math.ceil(total_amount))

                                if line.code == 'LOAN':
                                    loan_deduction_sum.append(math.ceil(total_amount))

                                if line.code == 'ARS':  #Arrear Allowance
                                    arrear_allowance_sum.append(math.ceil(total_amount))

                                if line.code == 'OAS':  # Other Allowance
                                    other_allowance_sum.append(math.ceil(total_amount))

                                if line.code == 'MOBILE':  # MOBILE Allowance
                                    mobile_allowance_sum.append(math.ceil(total_amount))

                                if line.code == 'SA':  # Special Allowance
                                    special_allowance.append(math.ceil(total_amount))

                                if line.code == 'EPMF':  # PF Contribution
                                    pf_contribution_sum.append(math.ceil(total_amount))

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

        for other_slip in docs.slip_ids:
            if not other_slip.employee_id.department_id.id:
                dpt_payslips = {}
                dpt_payslips['val'] = []

                payslip = {}
                payslip['sn'] = sn
                payslip['emp_name'] = other_slip.employee_id.name
                payslip['designation'] = other_slip.employee_id.job_id.name
                payslip['doj'] = other_slip.employee_id.initial_employment_date

                for rule in rule_list:
                    payslip[rule['code']] = 0
                    for line in other_slip.line_ids:
                        if line.code == rule['code']:
                            payslip[rule['code']] = math.ceil(line.total)

                            if line.code == "NET":
                                total_sum.append(math.ceil(line.total))

                            break;

                dpt_payslips['name'] = "Other"
                dpt_payslips['val'].append(payslip)

        all_total = sum(total_sum)

        gross_total_sum = sum(gross_total_sum)
        salary_deduc_total_sum = sum(salary_deduction_sum)
        mess_deduc_sum = sum(mess_deduction_sum)
        loan_deduc_sum = sum(loan_deduction_sum)
        arrears_tot_sum = sum(arrear_allowance_sum)
        other_allo_sum = sum(other_allowance_sum)
        mob_allw_sum = sum(mobile_allowance_sum)
        spec_allw_sum = sum(special_allowance)
        pf_tot_sum = sum(pf_contribution_sum)

        print '----------------- Total Gross amount: ', gross_total_sum
        print '----------------- Len',len(rule_list)



        dpt_payslips_list.append(dpt_payslips)
        amt_to_word = self.env['res.currency'].amount_to_word(float(all_total))

        locale.setlocale(locale.LC_ALL, 'bn_BD.UTF-8')
        thousand_separated_total_sum = locale.currency(all_total, grouping=True)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'hr.payslip.run',
            'docs': dpt_payslips_list,
            'docs_len': len(rule_list) + 8,
            'rules': rule_list,
            'total_sum': thousand_separated_total_sum,
            'amt_to_word': amt_to_word,
            'gross_total_sum': gross_total_sum,
            'salary_deduc_total_sum': abs(salary_deduc_total_sum),
            'mess_deduc_sum': abs(mess_deduc_sum),
            'loan_deduc_sum': abs(loan_deduc_sum),
            'arrears_tot_sum': arrears_tot_sum,
            'other_allo_sum': other_allo_sum,
            'mob_allw_sum': mob_allw_sum,
            'spec_allw_sum':spec_allw_sum,
            'pf_tot_sum': abs(pf_tot_sum),
            'data': data,
        }

        return self.env['report'].render('gbs_hr_payroll.report_individual_payslip', docargs)