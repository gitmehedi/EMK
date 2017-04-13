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
               
                if rule not in rule_list:
                    rule_list.append(rule)
                    
        sorted(rule.iteritems(), key=operator.itemgetter(1))
            
        payslips = []
        
        for slip in docs.slip_ids:
            
            payslip = {}
         
            payslip['emp_name'] = line.employee_id.name
            
            for emp in line.employee_id:            
                payslip['designation'] = emp.job_id.name
                payslip['doj'] = emp.initial_employment_date                  
            
            for line in slip.line_ids:
                for rule in rule_list:
                    if line.code == rule['code']:
                        payslip[line.code] = line.amount
                        
            payslips.append(payslip)
        
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'hr.payslip.run',
            'docs': payslips,
            'rules': rule_list,
        }
        return self.env['report'].render('gbs_hr_payroll.report_individual_payslip', docargs)
