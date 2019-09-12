# -*- coding: utf-8 -*-


from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class TrialBalanceXLSX(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, obj):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        display_account = docs['display_account']
        accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
        used_context = {
            'lang': self.env.context['lang'],
            'operating_unit_ids': docs['operating_unit_ids'].ids,
            'date_from': docs['date_from'],
            'date_to': docs['date_to'],
            'journal_ids': docs['journal_ids'].ids,
            'state': docs['target_move'],
            'strict_range': True,
        }
        account_res = self.env['report.account.report_trialbalance'].with_context(used_context)._get_accounts(
            accounts, display_account)

        header_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 12})
        format = workbook.add_format({'align': 'left', 'valign': 'top'})
        bold = workbook.add_format({'align': 'left', 'bold': True})
        no_format = workbook.add_format({'num_format': '#,###0.00'})

        worksheet = workbook.add_worksheet('Trial Balance')
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.merge_range('A1:F2', self.env.user.company_id.name + ': ' + self.title, header_format)

        if docs['display_account']:
            worksheet.write('B5', 'Display Accounts:', bold)
            if docs['display_account'] == 'all':
                display = 'All'
            elif docs['display_account'] == 'movement':
                display = 'With movements'
            else:
                display = 'With balance is not equal to 0'

            worksheet.write('B6', display)

        if docs['date_from']:
            worksheet.write('C5', 'Date From:', bold)
            worksheet.write('D5', docs['date_from'])
        if docs['date_to']:
            worksheet.write('C6', 'Date To:', bold)
            worksheet.write('D6', docs['date_to'])

        if docs['target_move']:
            worksheet.write('E5', 'Target Moves:', bold)
            target = 'All Entries' if docs['target_move'] == 'all' else 'All Posted Entries'
            worksheet.write('E6', target)

        if docs['operating_unit_ids']:
            worksheet.write('E8', 'Branch:', bold)
            worksheet.merge_range('E9:E10', ', '.join([val.name for val in docs['operating_unit_ids']]), format)

        row, col = 11, 0

        worksheet.write(row, col, 'Code', header_format)
        worksheet.write(row, col + 1, 'Account', header_format)
        worksheet.write(row, col + 2, 'Initial Balance', header_format)
        worksheet.write(row, col + 3, 'Debit', header_format)
        worksheet.write(row, col + 4, 'Credit', header_format)
        worksheet.write(row, col + 5, 'Closing Balance', header_format)

        row += 1
        for rec in account_res:
            worksheet.write(row, col, rec['code'])
            worksheet.write(row, col + 1, rec['name'])
            worksheet.write(row, col + 2, rec['init_bal'], no_format)
            worksheet.write(row, col + 3, rec['debit'], no_format)
            worksheet.write(row, col + 4, rec['credit'], no_format)
            worksheet.write(row, col + 5, (rec['debit'] - rec['credit']), no_format)
            row += 1


TrialBalanceXLSX('report.account_reports_xls.payroll_xls', 'account.balance.report', parser=report_sxw.rml_parse)
