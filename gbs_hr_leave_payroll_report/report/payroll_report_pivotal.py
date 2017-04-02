from openerp import api, exceptions, fields, models

    
class PayrollReportPivotal(models.AbstractModel):
    _name = 'report.gbs_hr_leave_payroll_report.report_absence_view_qweb'
    
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('hr_absence_summary.report_absence_view_qweb')
       
        self.env.cr.execute("CREATE extension tablefunc")
        all_values = self.env.cr.execute("SELECT * FROM crosstab ('SELECT employee_id, code, total FROM hr_payslip_line ORDER BY 1,2') AS final_result (employee_id integer,CA NUMERIC,NET NUMERIC,GROSS NUMERIC,MA NUMERIC,CAGG NUMERIC,HRA NUMERIC,BASIC NUMERIC,PF NUMERIC) ")
        
        print '---------------------------------------------------------', all_values
        
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': all_values,
            'form': data['form'],
            'other':data['other']
        }
        
        return report_obj.render('gbs_hr_leave_payroll_report.report_absence_view_qweb', docargs)
