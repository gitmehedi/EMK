from odoo import api, models, fields
from odoo.tools.misc import formatLang


class DailyUndeliveredStatementReport(models.AbstractModel):
    _name = "report.samuda_sales_report.report_daily_undelivered_statement"

    sql_str = """"""

    @api.multi
    def render_html(self, docids, data=None):
        report_data = self.get_data(data)
        docargs = {
            'data': data,
            'report_data': report_data,
            'formatLang': self.format_lang,
        }

        return self.env['report'].render('samuda_sales_report.report_daily_undelivered_statement', docargs)

    @api.multi
    def format_lang(self, value):
        return formatLang(self.env, value)

    @api.model
    def get_data(self, data):
        # Default report data
        report_data = {}

        return report_data
