from odoo import api, models, fields
from odoo.tools.misc import formatLang


class OutstandingStatementReport(models.AbstractModel):
    _name = "report.samuda_sales_report.report_outstanding_statement"

    sql_str_local = """"""

    @api.multi
    def render_html(self, docids, data=None):
        # data type list
        report_data = self.get_data(data)

        docargs = {
            'data': data,
            'report_data': report_data,
            'formatLang': self.format_lang,
        }

        return self.env['report'].render('samuda_sales_report.report_outstanding_statement', docargs)

    @api.multi
    def format_lang(self, value):
        return formatLang(self.env, value)

    @api.model
    def get_data(self, data):
        # Default report data
        report_data = list()

        # dummy data
        report_data.append({'sales_person': 'Didar', 'total_sale_value': 20000, 'credit_value': 5000, 'percentage': 5})
        report_data.append({'sales_person': 'Rafsan', 'total_sale_value': 20000, 'credit_value': 5000, 'percentage': 5})

        return report_data
