from odoo import api, exceptions, fields, models
import operator, math
import locale

class PayrollReportPivotal(models.AbstractModel):
    _name = 'report.gbs_hr_payroll_top_sheet.report_top_sheet'
    
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

        for d in dept:
            dpt_payslips = {}
            dpt_payslips['name'] = d.name
            dpt_payslips['val'] = []
            total_sum = 0
            count = 0
            payslip = {}
            for slip in docs.slip_ids:
                if d.id == slip.employee_id.department_id.id:
                    count +=1
            payslip['count_emp'] = count
            if payslip['count_emp'] == 0:
                continue;

            total_sum = []
            # payslip = {}
            for slip in docs.slip_ids:
                if d.id == slip.employee_id.department_id.id:
                    payslip['NET'] = 0
                    for line in slip.line_ids:
                        if line.code == 'NET':
                            total_amt = line.total
                            payslip['NET'] = math.ceil(total_amt)
                            total_sum.append(math.ceil(total_amt))
                            break;



            payslip['total_net'] = sum(total_sum)
            dpt_payslips['val'].append(payslip)
            dpt_payslips_list.append(dpt_payslips)



        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'hr.payslip.run',
            'docs': dpt_payslips_list,
            #'docs_len': len(rule_list)+8,
            # 'rules': rule_list,
            # 'total_sum': thousand_separated_total_sum,
            # 'amt_to_word': amt_to_word,
            'data': data,
        }
        
        return self.env['report'].render('gbs_hr_payroll_top_sheet.report_top_sheet', docargs)
    