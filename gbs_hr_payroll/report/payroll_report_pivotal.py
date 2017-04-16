from openerp import api, exceptions, fields, models
import operator

class PayrollReportPivotal(models.AbstractModel):
    _name = 'report.gbs_hr_payroll.report_individual_payslip'
    
    @api.model
    def render_html(self, docids, data=None):
        payslip_run_pool = self.env['hr.payslip.run']
        docs = payslip_run_pool.browse(docids[0])
        
        rule_list = []
        for slip in docs.slip_ids:
            for line in slip.line_ids:
                rule = {}
                rule['name'] = line.name
                rule['seq'] = line.sequence
                rule['code'] = line.code
                # line.employee_id.department_id.name

                if rule not in rule_list:
                    rule_list.append(rule)
                    
        sorted(rule.iteritems(), key=operator.itemgetter(1))
            
        dept = self.env['hr.department'].search([])
        dpt_payslips = dict((d.name,[]) for d in dept)

        payslips = []

        department_name = ''
        
        for slip in docs.slip_ids:
            
            payslip = {}
            payslip['emp_name'] = line.employee_id.name

            
            for emp in line.employee_id:            
                payslip['designation'] = emp.job_id.name
                payslip['doj'] = emp.initial_employment_date

            for line in slip.line_ids:
                for rule in rule_list:
                    if line.code == rule['code']:
                        department_name = line.employee_id.department_id.name
                        payslip[line.code] = line.amount

            if department_name in dpt_payslips:
                dpt_payslips[department_name].append(payslip)
                        
            # payslips.append(dpt_payslips)
            print "----", dpt_payslips
        
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'hr.payslip.run',
            'docs': dpt_payslips,
            'rules': rule_list,
        }
        return self.env['report'].render('gbs_hr_payroll.report_individual_payslip', docargs)
