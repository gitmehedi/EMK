from odoo import api,models,fields

class LoanReport(models.AbstractModel):
    _name = "report.hr_exit.report_employee_exit"

    @api.multi
    def render_html(self, docids, data=None):
        exit_obj = self.env['employee.exit.req'].browse(docids[0])

        data={}
        data['req_date'] = ''
        data['employee_id'] = ''
        data['last_date'] = ''