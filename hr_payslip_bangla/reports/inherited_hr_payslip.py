# -*- coding: utf-8 -*-
from odoo import api, models, fields
import bangla


class HRPayslipBanglaReport(models.AbstractModel):
    _name = 'report.hr_payslip_bangla.payslip_bangla_report'

    @api.multi
    def render_html(self, docids, data=None):

        payslip_obj = self.env['hr.payslip'].browse(docids[0])
        to_bangla_utility = self.env['to.bangla.utility']

        report_data = {}
        report_data['slip_name'] = payslip_obj.name
        if payslip_obj.employee_id.bangla_name:
            report_data['employee_name'] = payslip_obj.employee_id.bangla_name
        else:
            report_data['employee_name'] = payslip_obj.employee_id.name
        if payslip_obj.employee_id.work_email:
            report_data['employee_email'] = payslip_obj.employee_id.work_email
        else:
            report_data['employee_email'] = ''
        if payslip_obj.employee_id.job_id.bangla_name:
            report_data['employee_designation'] = payslip_obj.employee_id.job_id.bangla_name
        else:
            report_data['employee_designation'] = payslip_obj.employee_id.job_id.name
        if payslip_obj.employee_id.department_id.bangla_name:
            report_data['employee_department'] = payslip_obj.employee_id.department_id.bangla_name
        else:
            report_data['employee_department'] = payslip_obj.employee_id.department_id.name

        report_data['lines'] = []

        for line in payslip_obj.line_ids:
            dict_obj = {}

            dict_obj['salary_code'] = line.salary_rule_id.code
            if line.salary_rule_id.bangla_name:
                dict_obj['salary_bangla_name'] = line.salary_rule_id.bangla_name
            else:
                dict_obj['salary_bangla_name'] = line.salary_rule_id.name
            dict_obj['quantity'] = bangla.convert_english_digit_to_bangla_digit(("{:,.2f}".format(line.quantity)))
            dict_obj['amount'] = bangla.convert_english_digit_to_bangla_digit("{:,.2f}".format(line.amount))
            dict_obj['total'] = bangla.convert_english_digit_to_bangla_digit("{:,.2f}".format(line.total))

            if line.salary_rule_id.code == 'NET':
                try:
                    number = to_bangla_utility.input_sanitizer(float(line.total))
                    whole, fraction = to_bangla_utility.float_int_extraction(number)
                    whole_segments = to_bangla_utility.generate_segments(whole)
                    generated_words = to_bangla_utility.whole_part_word_gen(whole_segments)
                    if fraction and fraction > 0:
                        bangla_words = generated_words + " টাকা " + to_bangla_utility.fraction_to_words(
                            fraction) + " পয়সা "
                    else:
                        bangla_words = generated_words + " টাকা "

                    report_data['word_amount'] = bangla_words
                except:
                    report_data['word_amount'] = (self.env['res.currency'].amount_to_word(float(line.total)))

            report_data['lines'].append(dict_obj)

        docargs = {
            'data': report_data,
        }
        return self.env['report'].render('hr_payslip_bangla.payslip_bangla_report', docargs)
