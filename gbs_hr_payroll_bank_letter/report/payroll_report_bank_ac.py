from odoo import api, fields, models
import amount_to_text_bdt
import operator, math
from odoo.tools.misc import formatLang


class PayrollReportBankAc(models.AbstractModel):
    _name = 'report.gbs_hr_payroll_bank_letter.report_individual_payslip1'
    
    @api.model
    def render_html(self, docids, data=None):

        #payslip_run_pool = self.env['hr.payslip.run']
        slip_pool = self.env['hr.payslip']
        slip_ids = slip_pool.search([('payslip_run_id','=',data['active_id']),
                                     ('employee_id.bank_account_id.bank_id','=',data['bank_id'])])

        rule_list = []
        for slip in slip_pool.browse(slip_ids.ids):
            for line in slip.line_ids:
                rule = {}
                rule['name'] = line.name
                rule['seq'] = line.sequence
                rule['code'] = line.code

                if rule not in rule_list:
                    rule_list.append(rule)
                    
        rule_list = sorted(rule_list, key=lambda k: k['seq'])

        dpt_payslips_list = []
        total_sum = []
        sn = 1
        dpt_payslips = {}
        dpt_payslips['val'] = []
        emp_sort_list = None

        for slip in slip_pool.browse(slip_ids.ids):
            payslip = {}
            payslip['emp_name'] = slip.employee_id.name
            payslip['acc_no'] = slip.employee_id.bank_account_id.acc_number
            payslip['emp_seq'] = slip.employee_id.employee_sequence

            payslip['BNET'] = 0
            for line in slip.line_ids:
                if line.code == 'BNET':
                    total_amt = line.total
                    payslip['BNET'] = formatLang(self.env,math.ceil(total_amt))
                    total_sum.append(math.ceil(total_amt))
                    break;

            dpt_payslips['val'].append(payslip)
                    
        emp_sort_list  = dpt_payslips['val']
        emp_sort_list = sorted(emp_sort_list, key=lambda k: k['emp_seq'])
            
        for ps in emp_sort_list:
            ps['sn'] = sn
            sn += 1
            
        dpt_payslips['val'] = emp_sort_list
        dpt_payslips_list.append(dpt_payslips)
        total = sum(total_sum)
        all_total = formatLang(self.env,total)

        # Test Value
        # all_total = 1.11

        amt_to_word = self.env['res.currency'].amount_to_word(total)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'hr.payslip.run',
            'docs': dpt_payslips_list,
            'bank_name': data['bank_name'],
            'bank_street1':data['bank_street1'],
            'bank_street2': data['bank_street2'],
            'bank_city': data['bank_city'],
            'bank_zip': data['bank_zip'],
            'bank_country': data['bank_country'],
            'payslip_report_name': data['payslip_report_name'],
            'cur_year': data['cur_year'],
            'cur_month': data['cur_month'],
            'cur_day': data['cur_day'],
            'total_net': all_total,
            'docs_len': len(rule_list) + 4,
            'company': self.env['res.company']._company_default_get('gbs_hr_payroll_bank_letter').name,
            'amount_to_text_bdt': amt_to_word,
            'mother_bank_ac': data['mother_bank_ac'],
        }
        
        return self.env['report'].render('gbs_hr_payroll_bank_letter.report_individual_payslip1', docargs)
