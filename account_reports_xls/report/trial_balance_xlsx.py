# -*- coding: utf-8 -*-


from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class Payrollreport(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, obj):
        worksheet = workbook.add_worksheet()
        accounts = self.env['account.account'].search([])
        row = 0
        col = 0

        for rec in accounts:
            worksheet.write(row, col + 1, rec.name)
            worksheet.write(row, col + 3, rec.name)
            row += 1

Payrollreport('report.account_reports_xls.payroll_xls', 'account.balance.report',parser=report_sxw.rml_parse)
