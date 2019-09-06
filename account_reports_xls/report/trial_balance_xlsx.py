# -*- coding: utf-8 -*-


from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class TrialBalanceXLSX(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, obj):
        header_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 12})
        format = workbook.add_format({'align': 'left', 'size': 13})
        bold = workbook.add_format({'align': 'left', 'bold': True})
        no_format = workbook.add_format({'num_format': '#,###0.000'})

        worksheet = workbook.add_worksheet('Trial Balance')
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 15)

        worksheet.merge_range('A5:C10', 'Trial Balance', header_format)

        accounts = self.env['account.account'].search([])

        row = 10
        col = 0
        worksheet.write(row, col, 'Code', header_format)
        worksheet.write(row, col + 1, 'Account', header_format)
        worksheet.write(row, col + 2, 'Debit', header_format)
        worksheet.write(row, col + 3, 'Credit', header_format)
        worksheet.write(row, col + 4, 'Balance', header_format)

        row += 1
        for rec in accounts:
            worksheet.write(row, col, rec.code)
            worksheet.write(row, col + 1, rec.name)
            worksheet.write(row, col + 2, rec.debit, no_format)
            worksheet.write(row, col + 3, rec.credit, no_format)
            worksheet.write(row, col + 4, (rec.debit - rec.credit), no_format)
            row += 1


TrialBalanceXLSX('report.account_reports_xls.payroll_xls', 'account.balance.report', parser=report_sxw.rml_parse)
