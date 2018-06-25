from odoo import api,models,fields

class LoanReport(models.AbstractModel):
    _name = "report.hr_employee_loan.report_hr_employee_loan"

    @api.multi
    def render_html(self,docids,data=None):
        loan_obj = self.env['hr.employee.loan'].browse(docids[0])
        data = {}
        data['employee_name'] = loan_obj.employee_id.name


        docargs = {
            'data': data,

        }
        return self.env['re']