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
        #rule_list = sorted(rule_list, key=lambda k: k['seq'])

        dept = self.env['hr.department'].search([])
        dpt_payslips_list = []
        tot_gross = []
        tot_tds = []
        tot_epmf = []
        tot_mess = []
        tot_net = []
        tot_emp = []

        for d in dept:
            dpt_payslips = {}
            dpt_payslips['name'] = d.name
            dpt_payslips['val'] = []
            count = 0
            payslip = {}
            for slip in docs.slip_ids:
                if d.id == slip.employee_id.department_id.id:
                    count +=1
            payslip['count_emp'] = count
            if payslip['count_emp'] == 0:
                continue;

            total_sum = []
            tds_sum = []
            pf_sum = []
            mess_sum = []
            gross_sum = []
            for slip in docs.slip_ids:
                if d.id == slip.employee_id.department_id.id:
                    #payslip['NET'] = 0
                    for line in slip.line_ids:
                        if line.code == 'NET':
                            total_amt = line.total
                            total_sum.append(math.ceil(total_amt))
                        elif line.code == 'TDS':
                            total_tds = line.total
                            tds_sum.append(math.ceil(total_tds))
                        elif line.code == 'EPMF':
                            total_epmf = line.total
                            pf_sum.append(math.ceil(total_epmf))

                        elif line.code == 'MESS':
                            total_mess = line.total
                            mess_sum.append(math.ceil(total_mess))
                        elif line.code == 'GROSS':
                                gross_total = line.total
                                gross_sum.append(math.ceil(gross_total))

            payslip['gross'] = int(sum(gross_sum))
            payslip['total_net'] = int(sum(total_sum))
            payslip['tds'] = int(abs(sum(tds_sum)))
            payslip['epmf'] = int(abs(sum(pf_sum)))
            payslip['mess'] = int(abs(sum(mess_sum)))

            dpt_payslips['val'].append(payslip)
            dpt_payslips_list.append(dpt_payslips)
            tot_gross.append(int(abs(sum(gross_sum))))
            tot_tds.append(int(abs(sum(tds_sum))))
            tot_mess.append(int(abs(sum(mess_sum))))
            tot_epmf.append(int(abs(sum(pf_sum))))
            tot_net.append(int(abs(sum(total_sum))))
            tot_emp.append(count)

            # sum1= []
            # for j in dpt_payslips_list:
            #     sum1.append(j[payslip['mess']])
            # print sum1

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'hr.payslip.run',
            'docs': dpt_payslips_list,
            #'all_mess': all_mess,
            'data': data,
            'tot_gross' : sum(tot_gross),
            'tot_tds' : sum(tot_tds),
            'tot_mess' : sum(tot_mess),
            'tot_epmf' : sum(tot_epmf),
            'tot_net' : sum(tot_net),
            'tot_emp' : sum(tot_emp),
        }
        
        return self.env['report'].render('gbs_hr_payroll_top_sheet.report_top_sheet', docargs)
    