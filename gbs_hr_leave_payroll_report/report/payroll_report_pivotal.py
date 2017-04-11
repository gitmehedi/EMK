from openerp import api, exceptions, fields, models
    
class PayrollReportPivotal(models.AbstractModel):
    _name = 'report.gbs_hr_leave_payroll_report.report_absence_view_qweb'
    
    @api.model
    def render_html(self, docids, data=None):
        payslip_run_pool = self.env['hr.payslip.run']
        docs = payslip_run_pool.browse(docids[0])
        
        code_seq_dict = []
        
        for slip in docs.slip_ids:
            for line in slip.line_ids:
                if {line.code:line.sequence} not in code_seq_dict:
                    code_seq_dict.append({line.code:line.sequence})
                
                    code_seq_dict.sort()
            
        payslips = []
        
        for slip in docs.slip_ids:
            
            payslip = {}
         
            payslip['emp_name'] = line.employee_id.name
            
            for emp in line.employee_id:            
                payslip['designation'] = emp.job_id.name
                payslip['doj'] = emp.initial_employment_date                  
            
            for line in slip.line_ids:
                for rule in code_seq_dict:
                    if line.code == rule.keys()[0]:
                        payslip[line.code] = line.amount
                        
            payslips.append(payslip)
            
        print "=======================", payslip
        
        
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'hr.payslip.run',
            #'data': data['form'],
            'docs': payslips,
        }
        return self.env['report'].render('gbs_hr_leave_payroll_report.report_absence_view_qweb', docargs)
