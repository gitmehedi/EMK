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
            
        dept = self.env['hr.department'].search([])
        
        dpt_payslips_list = []
        for d in dept:
            
            dpt_payslips = {}
            dpt_payslips['name'] = d.name
            dpt_payslips['seq'] = d.sequence
            dpt_payslips['val'] = []
            
            for slip in docs.slip_ids:
                if d.id == slip.employee_id.department_id.id:
                    
                    payslip = {}
                    payslip['emp_name'] = slip.employee_id.name
        
                    payslip['designation'] = slip.employee_id.job_id.name
                    payslip['doj'] = slip.employee_id.initial_employment_date
        
                    for line in slip.line_ids:
                        for rule in rule_list:
                            if line.code == rule['code']:
                                payslip[line.code] = line.amount
                
                    dpt_payslips['val'].append(payslip)
                    dpt_payslips_list.append(dpt_payslips)
        
        #print '=====================================', docs.slip_ids
        

        if not docs.slip_ids.employee_id.department_id.id:
            payslip = {}
            payslip['emp_name'] = slip.employee_id.name

            payslip['designation'] = slip.employee_id.job_id.name
            payslip['doj'] = slip.employee_id.initial_employment_date

            for line in slip.line_ids:
                for rule in rule_list:
                    if line.code == rule['code']:
                        payslip[line.code] = line.amount

            dpt_payslips['name'] = "Other"
            dpt_payslips['val'].append(payslip)                  
            dpt_payslips_list.append(dpt_payslips)

        sorted(dpt_payslips.iteritems(), key=operator.itemgetter(1))
        
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'hr.payslip.run',
            'docs': dpt_payslips_list,
            'rules': rule_list,
        }
        
        return self.env['report'].render('gbs_hr_payroll.report_individual_payslip', docargs)
    