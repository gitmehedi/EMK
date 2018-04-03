from odoo import api, fields, models, _


class HrEmpLeaveReport(models.AbstractModel):
    _name = 'report.letter_of_credit_report.template_letter_of_credit_report'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']


        docargs = {
            'report_type': data['report_type'],

        }
        return report_obj.render('letter_of_credit_report.template_letter_of_credit_report', docargs)

