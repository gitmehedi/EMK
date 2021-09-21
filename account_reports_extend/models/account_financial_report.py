# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountFinancialReportLine(models.Model):
    _inherit = "account.financial.html.report.line"

    @api.constrains('code')
    def _code_constrains(self):
        super(AccountFinancialReportLine, self)._code_constrains()

        # Check for unique code
        if self.code:
            financial_report_lines = self.search([('code', '=ilike', self.code.strip())])
            if len(financial_report_lines.ids) > 1:
                raise ValidationError('Code must be unique!')
