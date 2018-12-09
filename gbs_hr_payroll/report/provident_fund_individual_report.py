import math
from odoo import api, exceptions, fields, models
from odoo.tools.misc import formatLang


class PfReport(models.AbstractModel):
    _name = 'report.gbs_hr_payroll.report_individual_provident_fund'

    @api.multi
    def render_html(self, docids, data=None):
        payslip_line = self.env['hr.payslip'].search([('employee_id', '=', data['emp_id']), ('state', '=', 'done')])
        pf_list = []
        for rec in payslip_line:
            pf_obj = {}
            for line in rec.line_ids:
                if line.code == 'EPMF':
                    pf_obj['name'] = rec.name
                    pf_obj['date'] = rec.date_from
                    pf_obj['pf'] = formatLang(self.env,math.ceil(abs(line.total)))
                    pf_list.append(pf_obj)

        docargs = {
            'doc_model': 'hr.payslip',
            'employee_id': data['employee_id'],
            'department_id': data['department_id'],
            'job_id': data['job_id'],
            'initial_employment_date': data['initial_employment_date'],
            'device_employee_acc': data['device_employee_acc'],
            'total_pf': formatLang(self.env,math.ceil(abs(data['total_pf']))),
            'lists': pf_list
        }
        return self.env['report'].render('gbs_hr_payroll.report_individual_provident_fund', docargs)
