from odoo import api, fields, models, _

class HrAttendanceErrorSummaryReport(models.AbstractModel):
    _name = 'report.hr_overtime_report.overtime_summary_report'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']

        docargs = {
            'data': data,
        }
        return report_obj.render('hr_overtime_report.overtime_summary_report', docargs)