from openerp import api, exceptions, fields, models
import operator, math

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
                    
        rule_list = sorted(rule_list, key=lambda k: k['seq'])
            
        dept = self.env['hr.department'].search([])
        
        dpt_payslips_list = []
        total_sum = []        
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
                    
                    for rule in rule_list:
                        payslip[rule['code']] = 0
                        for line in slip.line_ids:
                            if line.code == rule['code']:
                                total_amount = math.ceil(line.total)
                                payslip[rule['code']] = total_amount
                                                                
                                if line.code == "NET":
                                    total_sum.append(math.ceil(total_amount))
                                                                         
                                break;                        

                    dpt_payslips['val'].append(payslip)
                    
            emp_sort_list  = dpt_payslips['val']
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
        dpt_payslips_list.append(dpt_payslips)
        
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'hr.payslip.run',
            'docs': dpt_payslips_list,
            'docs_len': len(rule_list)+4,
            'rules': rule_list,
            'total_sum': all_total
        }
        
        return self.env['report'].render('gbs_hr_payroll.report_individual_payslip', docargs)
    