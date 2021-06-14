from odoo import api, models, fields
from odoo.tools.misc import formatLang


class ChequePrintReport(models.AbstractModel):
    _name = "report.gbs_cheque_management.report_cheque_print"

    @api.multi
    def render_html(self, docids, data=None):
        docargs = {
            'data': data,
            'formatLang': self.format_lang
        }

        return self.env['report'].render('gbs_cheque_management.report_cheque_print', docargs)

    @api.multi
    def format_lang(self, value):
        if value == 0:
            return value
        return formatLang(self.env, value)
