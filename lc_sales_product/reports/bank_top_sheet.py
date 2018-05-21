from odoo import api, fields, models, _

class BankTopSheet(models.AbstractModel):
    _name = 'report.lc_sales_product.hr_emp_leave_report'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']

        docargs = {
            'data': data,

        }
        return report_obj.render('gbs_hr_leave_report.hr_emp_leave_report', docargs)